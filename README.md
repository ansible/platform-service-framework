# Platform Service Framework

Platform Service Framework initializes Django projects based on templates and keep project updated
to follow the defined standards.

## Features

- Bootstrap new projects with `init`.
- Bootstrap new apps for the project with `init --apps`.
- Keep project updated with latest changes.
- Update every `apps/*` directory created from a framework template while
  preserving custom changes through Copier's conflict handling.
- Consolidates meta files such as pyproject, sonar, pre-commit, github actions, settings based on template standards + apps customizations.
- Validate the whole project structure.

Health endpoints should expose only coarse-grained check results such as
`ok` or `error`. Services that add custom health checks must log exception
details server-side and sanitize the response; health endpoints are public and
must not return database, connection, or other internal error details.


## Requirements

- git
- uv

## usage

### Start a new project named `my-project` with a single app named `api`

```console
$ uvx git+https://github.com/ansible/platform-service-framework init my-project
...
…………………………………………………………………………………………………………
Framework init finished
Created project at my-project/my_project
Created apps at my-project/apps/[api]
```
```
my-project
# Editable by developers
├── apps
│   ├── metadata/{pyproject,README,sonar,docs, AGENTS}
│   └── api/{viewsets,serializers,urls,permissions,settings...}.py

# Everything from here is not editable, will be overwritten by framework updates.
├── my_project
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── tests
│   ├── urls.py
│   └── wsgi.py
├── docs
│   └── templates
├── LICENSE
├── manage.py
├── AGENTS.md
├── pyproject.toml
├── README.md
└── sonar-project.properties
```

> Developers can edit files inside `apps`. Each app generated from a framework
> template records its own Copier answers, so subsequent updates can update
> the project and all managed apps. App-specific customizations may require
> conflict resolution during an update.

## What is included?

- UV based project
- Django > 5
- Django Ansible Base (dynamic)
- pytest 
- ruff
- ty 
- pdoc
- poethepoet

## How to manage the local project?


### Dependencies 

**UV** replaces PIP

```
uv sync
uv pip list
```


### Repo Tasks 

**Poe** replaces the makefile.

```console 
# list included tasks
$ uv run poe
```
```
Configured tasks:
  lint                  
  type_check            
  format                
  test                  
  check                 
  render-docs           
  serve-docs            
  clean
```

### Unit tests 

**UV** + **Poe** replaces tox.

```
uv run --isolated --python 3.12 pytest tests
```

### Docs 

**Pdoc** replaces sphinx 

It is **really** simple, and develper focused, THIS IS NOT SUPPOSED TO BE CUSTOMER DOCS.

Pdoc generates docs from README files and 
python docstrings, doc is maintained together 
with the code.

```
uv run poe serve-docs
```

### Format 

**Ruff** replaces linters and black.

```
uv run poe format 
```

### Type Checking

**Ty** Replaces Mypy 

```
uv run poe type_check
```
