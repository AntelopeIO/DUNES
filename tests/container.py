import os
import platform
import subprocess


class container:
    _container_name = ""
    _image_name = ""

    def __init__(self, container_name='dune_container', image_name='dune:latest'):
        self._container_name = container_name
        self._image_name = image_name
        self._debug = True

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
        return self._container_name

    def get_image(self):
        return self._image_name

    def execute_docker_cmd(self, cmd):
        with subprocess.Popen(['docker'] + cmd,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            stdout, stderr = proc.communicate()
            if self._debug:
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
        return self.execute_docker_cmd(
            ['cp', self._container_name + ":" + container_file, host_file])

    def cp_from_host(self, host_file, container_file):
        return self.execute_docker_cmd(
            ['cp', host_file, self._container_name + ":" + container_file])

    def rm_file(self, file_name):
        self.execute_cmd(['rm', '-rf', file_name])

    def find_pid(self, process_name):
        stdout, _, _ = self.execute_cmd(['ps', 'ax'])
        for line in stdout.splitlines(True):
            if "PID TTY" in line:
                continue
            if process_name in line:
                return line.split()[0]
        return -1

    def get_container_name(self):
        return self._container_name

    def commit(self, name):
        self.execute_docker_cmd(['commit', 'dune', 'dune'])

    def start(self):
        print("Starting docker container [" + self._container_name + "]")
        self.execute_docker_cmd(['container', 'start', self._container_name])

    def stop(self):
        print("Stopping docker container [" + self._container_name + "]")
        self.execute_docker_cmd(['container', 'stop', self._container_name])

    def destroy(self):
        print("Destroying docker container [" + self._container_name + "]")
        self.execute_docker_cmd(['container', 'stop', self._container_name])
        self.execute_docker_cmd(['container', 'rm', self._container_name])

    def execute_cmd_at(self, directory, cmd):
        with subprocess.Popen(['docker', 'container', 'exec', '-w', directory,
                               self._container_name] + cmd) as proc:
            proc.communicate()

    def execute_cmd(self, cmd):
        return self.execute_docker_cmd(
            ['container', 'exec', self._container_name] + cmd)

    def execute_interactive_cmd(self, cmd):
        with subprocess.Popen(['docker', 'container',
                               'exec', '-i', self._container_name] + cmd) as proc:
            proc.communicate()

    def execute_cmd2(self, cmd):
        with subprocess.Popen(['docker', 'container',
                               'exec', self._container_name] + cmd) as proc:
            proc.communicate()

    def execute_bg_cmd(self, cmd):
        return self.execute_cmd(cmd + ['&'])

    # possible values for the status: created, restarting, running, removing, paused, exited, dead
    def check_status(self, status):
        stdout, stderr, exit_code = self.execute_docker_cmd(['ps', '--filter',
                                                             'status=' + status])
        for line in stdout.splitlines(True):
            if "CONTAINER ID" in line:
                continue
            if self._container_name in line:
                return True
        return False

    # check if the container is still exists and was not deleted
    def exists(self):
        stdout, stderr, exit_code = self.execute_docker_cmd(['ps', '--filter',
                                                             'name=' + self._container_name])
        for line in stdout.splitlines(True):
            if "CONTAINER ID" in line:
                continue
            if self._container_name in line:
                return True
        return False

    # create a new container
    def create(self):
        print("Creating docker container [" + self._container_name + "]")
        self.execute_docker_cmd(["run", "--name=" + self._container_name,
                                 self._image_name, "exit"])
