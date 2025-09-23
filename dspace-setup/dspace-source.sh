#!/bin/bash

# =================================================
# MÓDULO DE CÓPIA DOS ARQUIVOS-FONTE
# =================================================
# dspace-source, version 1.0, UFPA | 2017

# Argumentos de entrada:
#	$1 - diretório 'home/$user' do usuário padrão do DSpace
#	$2 - nome do dspace-fonte acompanhado da versão

# Atribuições locais
home=$1
dspace_version=$2

# Import da biblioteca de verificação
source dspace-setup/verifier.sh

# Copia os arquivos de instação do DSpace para a pasta do usuário padrão
mkdir $home/$dspace_version
cp ./* $home/$dspace_version -R
writewarning $? "Problema ao copiar arquivos-fonte para a pasta do usuário"
