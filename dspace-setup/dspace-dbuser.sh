#!/bin/bash

# =================================================
# MÓDULO DE COMANDOS DE CRIAÇÃO DO BANCO DE DADOS
# =================================================
# dspace-userdb, version 1.5, UFPA | 2017

# Argumentos de entrada:
#	$1 - usuário de sistema admin do DSpace

# Atribuições locais
user=$1
password=$2

# Import da biblioteca de verificação
source dspace-setup/verifier.sh

# Cria e configura novo usuário de banco de dados
#echo 'Configure agora a senha para o banco de dados:'
#echo '[ATENÇÃO] Tenha certeza de usar a MESMA SENHA fornecida anteriormente para essa finalidade, do contrário o DSpace não se conectará ao banco de dados.'
#createuser -d -A -P $user
psql -c "CREATE ROLE $user ENCRYPTED PASSWORD '$password' NOSUPERUSER CREATEDB NOCREATEROLE INHERIT LOGIN;"
#checkloop $? "createuser -d -A -P $user"
