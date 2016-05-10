import os
import sublime

def disable_builtin_php():
    completions= os.path.join(sublime.packages_path(), 'PHP', 'PHP.sublime-completions')
    if not os.path.isfile(completions):
        os.makedirs(os.path.dirname(completions))
        with open(completions, 'w+') as file:
            file.write(str('// Builtin completions overridden by XP Framework'))
            file.write(str('// Delete this file to restore them'))

def plugin_loaded():
    disable_builtin_php()