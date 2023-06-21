import os
import platform
import subprocess
import tempfile


class docker_error(Exception):
    pass

IMAGES_BASE_URL = 'ghcr.io/antelopeio/'
CONTAINER_NAME = 'dunes_container'
IMAGE_NAME = 'dunes:latest'

class docker:

    _container = CONTAINER_NAME
    _image = None
    _cl_args = None
    _dunes_url = ""

    def __init__(self, container, image, cl_args):
        # pylint: disable=too-many-branches
        self._cl_args = cl_args
        if container is not None:
            self._container = container


        # Get list of all containers, search for this container in the list and set some values.
        container_found = False
        stdout,_,_ = self.execute_docker_cmd(['container', 'ls', '-a'])
        for line in stdout.split('\n'):
            if self._container in line:
                container_found = True
                entries = line.split()
                if len(entries) > 1:
                    self._image = entries[1]

        # Test to see if the container is running.
        container_running = False
        if container_found:
            # Get the list of running containers.
            stdout,_,_ = self.execute_docker_cmd(['container', 'ls'])
            container_running = self._container in stdout

        # Sanity check users image input.
        if image is not None:
            if self._image is None:
                self._image = image
            elif self._image != image:
                raise docker_error
            self._image = image

        # Set image name in the case user didn't set it and there's no container.
        if self._image is None:
            self._image = IMAGE_NAME

        # Set url.
        self._dunes_url = IMAGES_BASE_URL+self._image

        # No need to continue if the container is already running!
        if container_running:
            return

        # If we found the container, try to start it.
        if container_found:
            self.execute_docker_cmd(['container', 'start', self._container])
            # Get the list of running containers and see what our status is:
            stdout,stderr,_ = self.execute_docker_cmd(['container', 'ls'])
            if self._container in stdout:
                return
            raise docker_error(f"Failed to start {self._container}.\n{stderr}")

        # No container was found, so we need to start one.
        # Test to see if desired image is available locally.
        dunes_image = subprocess.check_output(['docker', 'images', '-q', self._image], stderr=None, encoding='utf-8')
        # Nope, try to download it.
        if dunes_image == '':
            print('Downloading DUNES image')
            self.upgrade()

        # Create the new container.
        print("Creating docker container [" + self._container + "]")
        host_dir = '/'
        if platform.system() == 'Windows':
            host_dir = 'C:/'
        self.execute_docker_cmd(['run',
            '-p', '127.0.0.1:8888:8888/tcp',
            '-p', '127.0.0.1:9876:9876/tcp',
            '-p', '127.0.0.1:8080:8080/tcp',
            '-p', '127.0.0.1:3000:3000/tcp',
            '-p', '127.0.0.1:8000:8000/tcp',
            '-v', host_dir + ':/host',
            '-d', '--name=' + self._container,
            self._image,
            'tail', '-f', '/dev/null'])


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

    def print_streams(self, stdout, stderr):
        if stdout is None and stderr is None:
            if self._cl_args.debug:
                print('No stdout/stderr info captured...')
            return

        print('================ STDOUT ================')
        print(stdout)
        print('================ STDERR ================')
        print(stderr)
        print('========================================')

    def execute_docker_cmd(self, cmd, *, check_status=True, capture_output=True):
        """Execute the given docker command in the active container.

        :param cmd: the command
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

        return stdout, stderr, status

    def file_exists(self, file_name):
        # not checking status code here because a non-zero status is a normal
        # occurrence, it just means that the file does not exist
        return self.execute_cmd(['test', '-f', file_name], check_status=False)[2] == 0

    def dir_exists(self, directory):
        # not checking status code here because a non-zero status is a normal
        # occurrence, it just means that the directory does not exist
        return self.execute_cmd(['test', '-d', directory], check_status=False)[2] == 0

    def file_has_string(self, file_name, str_regex, tail_file_only = False):
        # using check_status=False, because we do not want to raise docker_error
        # exception when the file does not have str_regex
        # if the file is too large, set tail_file_only = True
        # to search only the tail (last 10 lines) of the file
        grep_cmd =  'grep "' + str_regex + '" ' +  file_name
        if tail_file_only is True:
            grep_cmd = 'tail ' + file_name + ' | grep "' + str_regex + '"'
        # Has to make sure str_regex is double quoted !
        # print("[DEBUG] grep_cmd to execute:\t"+ grep_cmd +"\n")
        return self.execute_cmd(['bash', '-c', grep_cmd], check_status=False)[2] == 0

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

    def get_arch(self) :
        stdout, stderr, exit_code = self.execute_cmd(['uname', '-m'])
        if stdout in ('x86_64\n', 'amd64\n') :
            return 'amd64'
        if stdout in ('aarch64\n', 'arm64v8\n', 'arm64\n') :
            return 'arm64'
        raise NotImplementedError("Error, using an unsupported architecture")

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

    def commit(self):
        self.execute_docker_cmd(['commit', 'dunes', 'dunes'])

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
        # Pull the new image and give it a local tag.
        print(f"['docker', 'pull', {self._dunes_url}]")
        with subprocess.Popen(['docker', 'pull', self._dunes_url]) as proc:
            proc.communicate()
        if self._dunes_url != self._image:
            with subprocess.Popen(['docker', 'tag', self._dunes_url, self._image]) as proc:
                proc.communicate()
