import os
import json

class InMemoryFileSystem:
    def __init__(self):
        self.root = {'name': '/', 'type': 'directory', 'content': {}}
        self.current_directory = self.root

    def mkdir(self, dirname):
        new_dir = {'name': dirname, 'type': 'directory', 'content': {}}
        self.current_directory['content'][dirname] = new_dir

    def cd(self, path):
        if path == '/':
            self.current_directory = self.root
        elif path.startswith('/'):
            self._cd_absolute(path)
        else:
            self._cd_relative(path)

    def ls(self, path='.'):
        if path == '.':
            content = self.current_directory['content']
        elif path.startswith('/'):
            content = self._get_abs_path(path)['content']
        else:
            content = self._get_rel_path(path)['content']

        for name, item in content.items():
            print(name, end='  ')
        print()

    def grep(self, filename, pattern):
        file_content = self._get_file_content(filename)
        matches = [line for line in file_content if pattern in line]
        return matches

    def cat(self, filename):
        file_content = self._get_file_content(filename)
        print('\n'.join(file_content))

    def touch(self, filename):
        new_file = {'name': filename, 'type': 'file', 'content': []}
        self.current_directory['content'][filename] = new_file

    def echo(self, filename, text):
        file_content = self._get_file_content(filename)
        if isinstance(file_content, list):
            file_content.append(text)
        else:
            # If content is not a list (possibly a new file), create a list
            self.current_directory['content'][filename]['content'] = [text]

    def mv(self, source, destination):
        item = self._get_abs_path(source)
        del self._get_parent(destination)['content'][os.path.basename(source)]
        self._get_abs_path(destination)['content'][os.path.basename(source)] = item

    def cp(self, source, destination):
        item = self._get_abs_path(source).copy()
        self._get_abs_path(destination)['content'][os.path.basename(source)] = item

    def rm(self, path):
        del self._get_parent(path)['content'][os.path.basename(path)]

    def _get_abs_path(self, path):
        if path == '/':
            return self.root
        parts = path.split('/')[1:]
        current = self.root
        for part in parts:
            current = current['content'][part]
        return current

    def _get_rel_path(self, path):
        parts = path.split('/')
        current = self.current_directory
        for part in parts:
            if part == '..':
                current = self._get_parent(current['name'])
            else:
                current = current['content'][part]
        return current

    def _cd_absolute(self, path):
        self.current_directory = self._get_abs_path(path)

    def _cd_relative(self, path):
        self.current_directory = self._get_rel_path(path)

    def _get_parent(self, path):
        if path == '/':
            return None
        parts = path.split('/')
        parent_path = '/'.join(parts[:-1])
        return self._get_abs_path(parent_path)

    def _get_file_content(self, filename):
        return self._get_abs_path(filename)['content']

def save_state(file_system, path):
    with open(path, 'w') as file:
        json.dump(file_system.root, file)

def load_state(path):
    with open(path, 'r') as file:
        return json.load(file)

def main():
    file_system = InMemoryFileSystem()
    
    # Bonus: Check if the state needs to be loaded
    import sys
    args = sys.argv[1:]
    if args and args[0] == '--load':
        load_path = args[1]
        file_system.root = load_state(load_path)
        file_system.current_directory = file_system.root
    
    while True:
        command = input('> ')
        if command.lower() == 'exit':
            # Bonus: Check if the state needs to be saved
            if args and args[0] == '--save':
                save_path = args[1]
                save_state(file_system, save_path)
            break

        try:
            exec_command(file_system, command)
        except Exception as e:
            print(f"Error: {str(e)}")

def exec_command(file_system, command):
    if command.startswith('mkdir'):
        _, dirname = command.split()
        file_system.mkdir(dirname)
    elif command.startswith('cd'):
        _, path = command.split()
        file_system.cd(path)
    elif command.startswith('ls'):
        _, path = command.split() if len(command.split()) > 1 else (None, '.')
        file_system.ls(path)
    elif command.startswith('grep'):
        _, filename, pattern = command.split()
        matches = file_system.grep(filename, pattern)
        print('\n'.join(matches))
    elif command.startswith('cat'):
        _, filename = command.split()
        file_system.cat(filename)
    elif command.startswith('touch'):
        _, filename = command.split()
        file_system.touch(filename)
    elif command.startswith('echo'):
        _, rest_of_command = command.split(' ', 1)
        if (filename.startswith('"') and filename.endswith('"')) or (filename.startswith("'") and filename.endswith("'")):
            filename = filename[1:-1]
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            text = text[1:-1]
        if ' > ' in rest_of_command:
            filename, text = map(str.strip, rest_of_command.split(' > ', 1))
        else:
            filename, text = rest_of_command, ""
        file_system.echo(filename, text)
    elif command.startswith('mv'):
        _, source, destination = command.split()
        file_system.mv(source, destination)
    elif command.startswith('cp'):
        _, source, destination = command.split()
        file_system.cp(source, destination)
    elif command.startswith('rm'):
        _, path = command.split()
        file_system.rm(path)
    else:
        print(f"Unknown command: {command}")






if __name__ == "__main__":
    main()
