from __future__ import annotations


BASH_TEMPLATE = """\
%(function)s()
{
    local cur script coms opts com
    COMPREPLY=()
    _get_comp_words_by_ref -n : cur words

    # for an alias, get the real script behind it
    if [[ $(type -t ${words[0]}) == "alias" ]]; then
        script=$(alias ${words[0]} | sed -E "s/alias ${words[0]}='(.*)'/\\1/")
    else
        script=${words[0]}
    fi

    # lookup for command
    for word in ${words[@]:1}; do
        if [[ $word != -* ]]; then
            com=$word
            break
        fi
    done

    # completing for an option
    if [[ ${cur} == --* ]] ; then
        opts="%(opts)s"

        case "$com" in

%(cmds_opts)s

        esac

        COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
        __ltrim_colon_completions "$cur"

        return 0;
    fi

    # completing for a command
    if [[ $cur == $com ]]; then
        coms="%(cmds)s"

        COMPREPLY=($(compgen -W "${coms}" -- ${cur}))
        __ltrim_colon_completions "$cur"

        return 0
    fi
}

%(compdefs)s"""

ZSH_TEMPLATE = """\
#compdef %(script_name)s

%(function)s()
{
    local state com cur
    local -a opts
    local -a coms

    cur=${words[${#words[@]}]}

    # lookup for command
    for word in ${words[@]:1}; do
        if [[ $word != -* ]]; then
            com=$word
            break
        fi
    done

    if [[ ${cur} == --* ]]; then
        state="option"
        opts+=(%(opts)s)
    elif [[ $cur == $com ]]; then
        state="command"
        coms+=(%(cmds)s)
    fi

    case $state in
        (command)
            _describe 'command' coms
        ;;
        (option)
            case "$com" in

%(cmds_opts)s

            esac

            _describe 'option' opts
        ;;
        *)
            # fallback to file completion
            _arguments '*:file:_files'
    esac
}

%(function)s "$@"
%(compdefs)s"""

FISH_TEMPLATE = """\
function __fish%(function)s_no_subcommand
    for i in (commandline -opc)
        if contains -- $i %(cmds_names)s
            return 1
        end
    end
    return 0
end

# global options
%(opts)s

# commands
%(cmds)s

# command options

%(cmds_opts)s"""


POWERSHELL_TEMPLATE = (
    """\
$%(function)s = {
    param(
        [string] $wordToComplete,
        [System.Management.Automation.Language.Ast] $commandAst,
        [int] $cursorPosition
    )
    function Results($res) {
        return $res.GetEnumerator() | Where-Object { $_.Key -like "$wordToComplete*" } | ForEach-Object { [System.Management.Automation.CompletionResult]::new($_.Key,$_.Key,"ParameterValue",$_.Value) } 
    }
    $options = [ordered]@{%(opts)s}
    $commands = [ordered]@{%(cmds)s}

    if ($wordToComplete -eq "" -and ($commandAst.CommandElements.Count -eq 1)) {
        return Results ($commands + $options)
    }
    if ($wordToComplete -notlike '--*' -and $wordToComplete -notlike "" -and """
    """($commandAst.CommandElements.Count -eq "2")) {
        return Results $commands
    }

    $result = $commandAst.CommandElements | Select-Object -Skip 1 | """
    """Where-Object { $_ -notlike '--*' }
    switch ($result -Join " " ) {
%(cmds_opts)s
    }

    return Results ($option + $options)
}

Register-ArgumentCompleter -Native -CommandName %(script_name)s """
    """-ScriptBlock $%(function)s"""
)

TEMPLATES = {
    "bash": BASH_TEMPLATE,
    "zsh": ZSH_TEMPLATE,
    "fish": FISH_TEMPLATE,
    "PowerShell": POWERSHELL_TEMPLATE,
}
