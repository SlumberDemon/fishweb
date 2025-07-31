# Process Apps

Process based apps are able to use any framework and language as long as you can run them through a CLI!

## Running

In order to start the app process you need to configure the command to run the it, this is done in the `fishweb.yaml` file.
Add the [`run_cmd`](/content/reference/app-config#run) field with your command.

For fishweb to properly serve/proxy your app it either needs to be able to provide it a port or you need to set the port in fishweb.
The easier method is having fishweb generate the port for the app as it also makes sure it's free.

To have fishweb generate the port for your add `$PORT` to the `run_cmd` field, fishweb will replace this with the generated port.
Or if you want to set the port add [`port`](/content/reference/app-config#port) to your config.

### Current working directory

As process are started and run using only whats in the apps root dir you may encounter an error when trying to use a cli tool to start your service that isn't included in your apps folder. To be able to use cli outside the cwd, add the whole path.

For example if you want to use `uv` on it's own it will error but if you add the path like `/user/local/bin/uv` it will work. On unix based systems you can run `which uv` to get the path. If your planning to run a python app with a venv, find out more [here](/content/concepts/venv#running-using-a-virtual-environment)
