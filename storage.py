import docker


class Storage(object):
    """
    Docker client wrapper.
    Manages different storage instances
    """

    def __init__(self):
        self._client = docker.from_env()
        self._cont_list = []

    @property
    def running_containers(self):
        """List of storage containers in running state"""
        return self._cont_list

    def close(self):
        """Closes docker client connection"""
        self._client.close()

    def stop_all(self):
        """Stops all storage containers"""
        cont_list = self.running_containers.copy()
        for c in cont_list:
            try:
                c.stop()
            finally:
                self.running_containers.remove(c)
        del cont_list

    def run(self, name, image, port):
        """Initializes specified storage instance running in docker container"""
        try:
            c = self._client.containers.get(name)
            c.restart()
            self._cont_list.append(c)
        except docker.errors.NotFound:
            self._client.containers.run(
                image=image,
                detach=True,
                name=name,
                ports={
                    port: port
                }
            )