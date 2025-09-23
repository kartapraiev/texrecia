#!/bin/bash

# =================================================
# MÓDULO DE INSTALAÇÃO DOS ARQUIVOS-BASE
# =================================================
# dspace-install, version 1.0, UFPA | 2017

# Argumentos de entrada:
#	$1 - diretório 'home/$user' do usuário padrão do DSpace
#	$2 - nome do dspace-fonte acompanhado da versão

# Atribuições locais
home=$1
dspace_version=$2

# Import da biblioteca de verificação
source dspace-setup/verifier.sh

# Instala o dspace no diretório-base [usa Apache Ant]
cd $home/$dspace_version/dspace/target/dspace-*
writewarning $? "Não foi possível acessar o diretório '$home/$dspace_version/dspace/target/dspace-installer'"
$home/apache-ant/bin/ant fresh_install
writeerror $? "Problema na instalação do sistema [Apache Ant]"