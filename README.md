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

For a while, I had been using a `this.org` pattern for my ad-hoc org files.
Say I was in a directory that was a repo for a project I was on and suddenly
needed to take notes- I'd do a `vim .this.org` and write my notes in it. Or
say I was configuring something in the system and needed to take notes on
what I was doing- Again, I'd do a `vim .this.org`.

This pattern worked well because I'd always be able to have contextual org-mode
note files wherever I was. But it had a number of downsides.

For one, it littered my directories with `.this.org` files. If a directory
was a repo, I'd generally have to add `.this.org` to its ignore file. Further,
I'd have no way to easily backup or version control all of my `.this.org` files.

I created a hacky shell script that would let me have system-wide org-mode files
in my home-directory that would be associated by hashes of the directories I
was in. This let me keep my `this.org` pattern, but not litter my directories.
It also let me version control my `this.org` files and back them up easily.

Originally, this shell script was called `torg` (from `this.org`). As I started
refining it, and extending it, I eventually decided I should re-write it in
Python. Since I was a MST3k fan, and since Manos The Hands of Fate is the
greatest movie of all time, it was an easy leap to go from `this.org`, to `torg`,
to `torgo`.
