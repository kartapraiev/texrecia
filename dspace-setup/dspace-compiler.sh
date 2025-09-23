#!/bin/bash

# =================================================
# MÓDULO DE COMPILAÇÃO DO DSPACE
# =================================================
# dspace-compiler, version 1.0, UFPA | 2017

# Argumentos de entrada:
#	$1 - diretório 'home/$user' do usuário padrão do DSpace
#	$2 - nome do dspace-fonte acompanhado da versão

# Atribuições locais
home=$1
dspace_version=$2

# Import das bibliotecas de diálogo e verificação
source dspace-setup/verifier.sh

# Compila o DSpace [usa Apache Maven]
cd $home/$dspace_version
writewarning $? "Não foi possível acessar o diretório '$home/$dspace_version'"
$home/apache-maven/bin/mvn -U clean package
writeerror $? "Problema na compilação do código-fonte [Apache Maven]"
