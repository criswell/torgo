<p align="center"><img src="torgo.jpg" /></p>

Torgo is the system-wide org file manager. It allows you to create org-mode
files that are associated with whatever directory you are in, but which are
managed externally.

# Usage

```
usage: torgo [-h] [-t] [-i] [-p]

Org-file anywhere, managed

optional arguments:
  -h, --help   show this help message and exit
  -t, --this   Use 'this' directory, don't attempt to find org file in parents
  -i, --init   Force a re-init of the configuration
  -p, --prune  Prune the current org file (delete it)
```

Wherever you run torgo, torgo will create a managed org-mode file for the
directory you are in. This org-mode file will be stored in a central location,
but will be associated with the directory torgo was called from.

## Configuration

When torgo is first ran, it will walk you through a configuration file
creation process. This configuration file defaults to `~/.torgo.cfg`, but you
can override that with the `$TORGO_CFG` environment variable.

The config file defines the following settings:

* `org_dir` : This is the path to where your org files will go. It defaults
to `~/.torgo/`.
* `editor` : This is your desired text editor. If blank, will attempt to use
`$EDITOR` from your environment.
* `ext` : This is the desired org file extension. It defaults to `org`.

You can force torgo to re-initialize the configuration by passing the
`-i`/`--init` option.

# Why is it called Torgo?


