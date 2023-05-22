import os
import platform
import subprocess
import tempfile


class docker:

    _container = ""
    _image = ""
    _cl_args = None
    _dune_url = 'ghcr.io/antelopeio/dune:latest'

    def __init__(self, container, image, cl_args):
        self._container = container
        self._image = image
        self._cl_args = cl_args

        # check if container is running
        stdout, stderr, exit_code = self.execute_docker_cmd(['container', 'ls'])

        # if container is not in the list then create one
        if self._container not in stdout:
            # check if container is stopped
            stdout, stderr, exit_code = self.execute_docker_cmd(
                ['container', 'ls', '-a'])
            if self._container in stdout:
                self.execute_docker_cmd(
                    ['container', 'start', self._container])
            else:
                # download dune image
                dune_image = subprocess.check_output(['docker', 'images', '-q', self._image], stderr=None, encoding='utf-8')

                if dune_image == '':
                    print('Downloading Dune image')
                    self.upgrade()
                    with subprocess.Popen(['docker', 'tag', self._dune_url, 'dune:latest']) as proc:
                        proc.communicate()


                # start a new container
                print("Creating docker container [" + self._container + "]")
                host_dir = '/'
                if platform.system() == 'Windows':
                    host_dir = 'C:/'

                stdout, stderr, exit_code = self.execute_docker_cmd(
                    ['run', '-p', '127.0.0.1:8888:8888/tcp', '-p', '127.0.0.1:9876:9876/tcp', '-p',
                     '127.0.0.1:8080:8080/tcp', '-p', '127.0.0.1:3000:3000/tcp', '-p', '127.0.0.1:8000:8000/tcp', '-v',
                     host_dir + ':/host', '-d', '--name=' + self._container,
                     self._image, 'tail', '-f', '/dev/null'])

    @staticmethod
    def abs_host_path(directory):
        abs_path = os.path.abspath(directory)
        if platform.system() == 'Windows':
            # remove the drive letter prefix and replace the separators
            abs_path = abs_path[3:].replace('\\', '/')
        else:
            abs_path = abs_path[1:]

        return '/host/' + abs_path

    def get_container(self):
        return self._container

    def get_image(self):
        return self._image

    def execute_docker_cmd(self, cmd):
        with subprocess.Popen(['docker'] + cmd,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            stdout, stderr = proc.communicate()
            if self._cl_args.debug:
                print('docker '+' '.join(cmd))
                print(stdout.decode('UTF-8'))
                print(stderr.decode('UTF-8'))
        return [stdout.decode('UTF-8'), stderr.decode('UTF-8'), proc.poll()]

    def file_exists(self, file_name):
        return self.execute_cmd(['test', '-f', file_name])[2] == 0

    def dir_exists(self, directory):
        return self.execute_cmd(['test', '-d', directory])[2] == 0

    def tar_dir(self, file_name, directory):
        return self.execute_cmd(['tar', 'cvzf', file_name + '.tgz', directory])

    def untar(self, directory):
        return self.execute_cmd(['tar', 'xvzf', directory])

    def cp_to_host(self, container_file, host_file):
        return self.execute_docker_cmd(['cp', self._container + ":" + container_file, host_file])

    def cp_from_host(self, host_file, container_file):
        return self.execute_docker_cmd(['cp', host_file, self._container + ":" + container_file])

    def rm_file(self, file_name):
        self.execute_cmd(['rm', '-rf', file_name])

    def write_file(self, file_name, body):
        tmp_name = ""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            tmp.write(body)
            tmp.flush()
            tmp_name = tmp.name

        self.cp_from_host(tmp_name, file_name)
        os.unlink(tmp_name)

    def find_pid(self, process_name):
        stdout, stderr, exit_code = self.execute_cmd(['ps', 'ax'])
        for line in stdout.splitlines(True):
            if "PID TTY" in line:
                continue
            if process_name in line:
                return line.split()[0]
        return -1

    def get_container_name(self):
        return self._container

    def commit(self, name):
        self.execute_docker_cmd(['commit', 'dune', 'dune'])

    def start(self):
        print("Starting docker container [" + self._container + "]")
        self.execute_docker_cmd(['container', 'start', self._container])

    def stop(self):
        print("Stopping docker container [" + self._container + "]")
        self.execute_docker_cmd(['container', 'stop', self._container])

    def destroy(self):
        print("Destroying docker container [" + self._container + "]")
        self.execute_docker_cmd(['container', 'stop', self._container])
        self.execute_docker_cmd(['container', 'rm', self._container])

    def execute_cmd_at(self, directory, cmd):
        with subprocess.Popen(['docker', 'container', 'exec', '-w', directory,
                               self._container] + cmd) as proc:
            proc.communicate()

    def execute_cmd(self, cmd):
        return self.execute_docker_cmd(
            ['container', 'exec', self._container] + cmd)

    def execute_interactive_cmd(self, cmd):
        with subprocess.Popen(['docker', 'container',
                               'exec', '-i', self._container] + cmd) as proc:
            proc.communicate()

    def execute_cmd2(self, cmd):
        with subprocess.Popen(['docker', 'container',
                               'exec', self._container] + cmd) as proc:
            proc.communicate()

    def execute_bg_cmd(self, cmd):
        return self.execute_cmd(cmd + ['&'])

    def upgrade(self):
        with subprocess.Popen(['docker', 'pull', self._dune_url]) as proc:
            proc.communicate()
