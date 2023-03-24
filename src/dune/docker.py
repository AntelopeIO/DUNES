import os
import platform
import subprocess


class docker_error(Exception):
    pass


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
                    ['run', '-p', '8888:8888', '-p', '9876:9876', '-p',
                     '8080:8080', '-p', '3000:3000', '-p', '8000:8000', '-v',
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

    @staticmethod
    def print_streams(stdout, stderr):
        if stdout is None and stderr is None:
            print('!! No stdout/stderr info captured...')
            return

        print('================ STDOUT ================')
        print(stdout)
        print('================ STDERR ================')
        print(stderr)
        print('========================================')

    def execute_docker_cmd(self, cmd, *, check_status=True, capture_output=True):
        """Execute the given docker command in the active container.

        :param check_status: if command has a return code != 0 then raise an exception
        :param capture_output: whether to capture stdout and stderr and return them or to
                               print the streams normally
        :return: (stdout, stderr, status_code) if captured, (None, None, status_code) otherwise
        """
        if capture_output:
            with subprocess.Popen(['docker'] + cmd,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
                stdout, stderr = proc.communicate()
                stdout = stdout.decode('UTF-8')
                stderr = stderr.decode('UTF-8')
                status = proc.returncode

        else:
            with subprocess.Popen(['docker'] + cmd) as proc:
                proc.communicate()
                stdout = None
                stderr = None
                status = proc.returncode

        if check_status and status != 0:
            # some error happened, log it and fail
            print(f'ERROR: docker {cmd}  -- returned: {status}')
            self.print_streams(stdout, stderr)
            raise docker_error

        if self._cl_args.debug:
            print('docker '+' '.join(cmd))
            self.print_streams(stdout, stderr)

        return (stdout, stderr, status)

    def file_exists(self, file_name):
        return self.execute_cmd(['test', '-f', file_name], check_status=False)[2] == 0

    def dir_exists(self, directory):
        return self.execute_cmd(['test', '-d', directory], check_status=False)[2] == 0

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

    def execute_cmd(self, cmd, *, interactive=False, colors=False, chdir=None, **kwargs):
        docker_cmd = ['container', 'exec']
        if interactive:
            docker_cmd += ['-i']
        if colors:
            docker_cmd += ['-t', '-e', 'TERM=xterm-256color']
        if chdir is not None:
            docker_cmd += ['-w', chdir]
        docker_cmd += [self._container]
        return self.execute_docker_cmd(docker_cmd + cmd, **kwargs)

    def execute_interactive_cmd(self, cmd, **kwargs):
        self.execute_cmd(cmd, interactive=True,
                         capture_output=False, **kwargs)

    def execute_bg_cmd(self, cmd):
        return self.execute_cmd(cmd + ['&'])

    def upgrade(self):
        with subprocess.Popen(['docker', 'pull', self._dune_url]) as proc:
            proc.communicate()
