import os
import sublime
import sublime_plugin
import subprocess
import os

class XpFormat(sublime_plugin.TextCommand):
    def is_enabled(self):
        return self.view.match_selector(0, 'embedding.php')

    def run(self, edit):

        # Sort imports
        uses = self.view.find_all('^use [^;]+;')
        if not uses:
            return

        imports = {'local' : [], 'remote': [], 'symbol' : []}
        for match in uses:
            line = self.view.substr(match)
            if line.find(' function ') > -1:
                kind = 'symbol'
            elif line.find(' const ') > -1:
                kind = 'symbol'
            elif line.find(' from ') > -1:
                kind = 'remote'
            else:
                kind = 'local'

            imports[kind].append(line)


        lines = ''
        for kind in ['local', 'remote', 'symbol']:
            listof = imports[kind]
            if listof:
                listof.sort()
                lines += "\n".join(listof) + "\n\n"

        self.view.replace(edit, sublime.Region(uses[0].begin(), uses[len(uses) - 1].end()), lines.rstrip())


class CompleteTypes(sublime_plugin.EventListener):
     def on_pre_save(self, view):
        if not view.match_selector(0, 'embedding.php'):
            return

        print('>> Saving ' + view.file_name())
        view.run_command('xp_format')

     def on_query_completions(self, view, prefix, locations):
        if view.file_name() is None:
            return

        completions = []

        line = view.substr(view.line(view.sel()[0]));
        if line.startswith('use '):
            dotted = line.replace('\\', '.')
            package = dotted[4:-len(prefix) - 1]
            search = dotted[4:-1]

            # Find base path
            base = os.path.dirname(view.file_name())
            while not os.path.isfile(os.path.join(base, 'composer.json')):
                parent = os.path.dirname(base)
                if os.path.samefile(parent, base):
                    break
                base = parent

            print('>> ' + dotted + '* @ ' + base);

            # Start process
            if os.name == 'nt':
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW 
                info.wShowWindow = subprocess.SW_HIDE
            else:
                info = None

            command = 'xp "' + os.path.join(os.path.dirname(__file__), 'types.script.php') + '" "' + package + '"';
            try:
                proc = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    startupinfo=info,
                    cwd=base
                )
                output, error = proc.communicate()

                # Transform output
                for line in output.decode().split("\n"):
                    if (line.startswith(search)):
                        completions.append(line.split('>>'));

                return completions
            except FileNotFoundError as e:
                sublime.status_message(str(e) + ' @ ' + command)
                return []

def disable_builtin_php():
    completions= os.path.join(sublime.packages_path(), 'PHP', 'PHP.sublime-completions')
    if not os.path.isfile(completions):
        os.makedirs(os.path.dirname(completions))
        with open(completions, 'w+') as file:
            file.write(str('// Builtin completions overridden by XP Framework'))
            file.write(str('// Delete this file to restore them'))

def plugin_loaded():
    disable_builtin_php()