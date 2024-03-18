#!bash

# Bash script to setup a new CookieList project
#
# $1 == CookieList Repository Name (e.g. gh_username/repo_name)
# $2 == CookieList Repository Branch (e.g. "main", "staging")
# $3 == CookieList Project App Id (e.g. cookielist-core-or-stub-app)
# $4 == Empty Directory Warning (e.g. "Yes" or "No")
# $5 == Is Developent version? (e.g. "Yes" or "No")
# $6 == DotEnv Key (e.g. dotenv://:key_dotenv_project_hash_id@dotenv.org/vault/.env.vault?environment=environment_id)


CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
DIRECTORY=$(pwd)

echo -e "${CYAN}[${NC}${GREEN}CookieList${NC}${CYAN}] Project Setup Script.${NC}"

REPOSITORY=$1
if [ -z "$REPOSITORY" ]; then
    DEFAULT_REPOSITORY="CookieList/cookielist.app"
    echo -e -n "${CYAN}Enter CookieList Repository Name${NC} [${GREEN}$DEFAULT_REPOSITORY${NC}]: "
    read REPOSITORY
    if [ -z "$REPOSITORY" ]; then
        REPOSITORY="$DEFAULT_REPOSITORY"
    fi
fi

BRANCH=$2
if [ -z "$BRANCH" ]; then
    DEFAULT_BRANCH="main"
    echo -e -n "${CYAN}Enter CookieList Branch Name${NC} [${GREEN}$DEFAULT_BRANCH${NC}]: "
    read BRANCH
    if [ -z "$BRANCH" ]; then
        BRANCH="$DEFAULT_BRANCH"
    fi
fi

COOKIELIST_APP=$3
if [ -z "$COOKIELIST_APP" ]; then
    echo -e -n "${CYAN}Enter CookieList App Id${NC}: "
    read COOKIELIST_APP
fi

if [[ -d "$DIRECTORY" && -n "$(ls -A "$DIRECTORY")" ]]; then
    CHOICE=$4
    if [ -z "$CHOICE" ]; then
        echo -e "${YELLOW}Warning:${NC} Current Directory Is Not Empty."
        echo -e -n "${CYAN}Empty '$DIRECTORY'${NC} [${GREEN}Yes/(No)${NC}]: "
        read CHOICE
    fi
    
    case $CHOICE in
        "YES" | "yes" | "Yes" | "Y" | "y")
            echo -e "${CYAN}Info:${NC} Clearing Curret Directory."
            find "$DIRECTORY" -mindepth 1 -exec rm -rf -- {} +
            if [ $? -eq 0 ]; then
                echo -e "${CYAN}Info:${NC} Curret Directory Cleared Successfully"
            else
                echo -e "${RED}Error:${NC} Directory Clearing Failed, Terminated Setup."
                exit 1
            fi
        ;;
        "NO" | "no" | "No" | "N" | "n")
            echo -e "${YELLOW}Warning:${NC} Repository Cloning Require Empty Directory."
            echo -e "${CYAN}Info:${NC} Exiting Setup."
            exit
        ;;
        *)
            echo -e "${RED}Error:${NC} Invalid Input, Terminated Setup."
            exit 1
        ;;
    esac
fi

DEV_VERSION=$5
if [ -z "$DEV_VERSION" ]; then
    echo -e -n "${CYAN}Is Dev version${NC}: "
    read DEV_VERSION
    case $DEV_VERSION in
        "YES" | "yes" | "Yes" | "Y" | "y" | "true")
            DEV_VERSION="true"
        ;;
        "NO" | "no" | "No" | "N" | "n" | "false")
            DEV_VERSION="false"
        ;;
        *)
            echo -e "${RED}Error:${NC} Invalid Input, Terminated Setup."
            exit 1
        ;;
    esac
fi

DOTENV_KEY=$6
if [ -z "$DOTENV_KEY" ]; then
    echo -e -n "${CYAN}Enter DotEnv Key${NC}: "
    read DOTENV_KEY
fi

git clone --branch $BRANCH "https://github.com/$REPOSITORY.git" "$DIRECTORY"

if [ $? -eq 0 ]; then
    echo -e "${CYAN}Info:${NC} Cloned Repository 'https://github.com/$REPOSITORY.git' ($BRANCH) At '$DIRECTORY'"
    
    if [ -f "$DIRECTORY/requirements.txt" ]; then
        python -m pip install --no-cache-dir -r "$DIRECTORY/requirements.txt"
        
        if [ $? -eq 0 ]; then
            echo -e "${CYAN}Info:${NC} Dependencies Installed Successfully."
        else
            echo -e "${RED}Error:${NC} Failed To Install Dependencies."
        fi
        
        if [ "$DEV_VERSION" == "true" ]; then
            if [ -f "$DIRECTORY/requirements.dev.txt" ]; then
                python -m pip install --no-cache-dir -r "$DIRECTORY/requirements.dev.txt"
                
                if [ $? -eq 0 ]; then
                    echo -e "${CYAN}Info:${NC} Dev Dependencies Installed Successfully."
                else
                    echo -e "${RED}Error:${NC} Failed To Install Dev Dependencies."
                fi
            else
                echo -e "${YELLOW}Warning:${NC} No requirements.dev.txt Found In The Repository."
            fi
        fi
    else
        echo -e "${YELLOW}Warning:${NC} No requirements.txt Found In The Repository."
    fi
    
    echo -e "${CYAN}Info:${NC} Creating app.py"
    {
        echo "#!/usr/bin/env python"
        echo ""
        echo "# This file is part of the 'CookieList' project."
        echo "# automatically created by setup.sh on '$(date)'."
        echo "# with the github repository https://github.com/$REPOSITORY.git ($BRANCH)"
        echo ""
        echo "import os"
        echo "os.environ['DOTENV_KEY'] = '$DOTENV_KEY'"
        echo ""
        echo "from cookielist.__main__ import get_app"
        echo "app = get_app('$COOKIELIST_APP')"
        echo ""
    } > "$DIRECTORY/app.py"
    
    echo -e "${CYAN}Info:${NC} Creating update.sh"
    {
        echo "#!/usr/bin/env bash"
        echo ""
        echo "# This file is part of the 'CookieList' project."
        echo "# automatically created by setup.sh on '$(date)'."
        echo "# with the github repository https://github.com/$REPOSITORY.git ($BRANCH)"
        echo ""
        echo "cd \"$DIRECTORY\""
        echo "curl -L https://raw.githubusercontent.com/$REPOSITORY/$BRANCH/setup.sh | bash -s -- $REPOSITORY $BRANCH $COOKIELIST_APP yes $DEV_VERSION $DOTENV_KEY"
        echo ""
    } > "$DIRECTORY/update.sh"
    
    echo -e "${CYAN}Info:${NC} Removing Unnecessary Files."
    rm -rf "$DIRECTORY/.git" "$DIRECTORY/.github" "$DIRECTORY/requirements.dev.txt" "$DIRECTORY/requirements.txt" "$DIRECTORY/setup.sh" "$DIRECTORY/run.sh" "$DIRECTORY/README.md" "$DIRECTORY/.gitignore" # "$DIRECTORY/LICENSE" "$DIRECTORY/docs"
    
    echo -e "${GREEN}Success:${NC} Setup Completed Successfully."
    
else
    echo -e "${RED}Error:${NC} Failed To Clone The Repository."
fi
