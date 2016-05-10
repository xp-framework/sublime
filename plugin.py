import os
import sublime
import sublime_plugin
import subprocess
import os

class CompleteTypes(sublime_plugin.EventListener):
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

            proc = subprocess.Popen(
                'xp "' + os.path.join(os.path.dirname(__file__), 'types.script.php') + '" "' + package + '"',
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

def disable_builtin_php():
    completions= os.path.join(sublime.packages_path(), 'PHP', 'PHP.sublime-completions')
    if not os.path.isfile(completions):
        os.makedirs(os.path.dirname(completions))
        with open(completions, 'w+') as file:
            file.write(str('// Builtin completions overridden by XP Framework'))
            file.write(str('// Delete this file to restore them'))

def plugin_loaded():
    disable_builtin_php()