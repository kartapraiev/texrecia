#!/bin/bash

# =================================================
# DSPACE INSTALLER
# =================================================
# Descrição:
# 	Script desenvolvido para automatizar o processo de instalação do DSpace. Este script foi desenvolvido
#	utilizando a configuração do servidor do Dspace com Debian 8.7.1 jessie 64bit; não garantimos que ele
#	irá funcionar como esperado em outras versões ou distros do Sistema Operacional. Se você tiver insta-
#	lado qualquer outra versão anterior do DSpace, remova-a completamente para evitar conflitos, bem como
#	todos os softwares auxiliares. Para migração do banco de dados consulte
#	https://wiki.duraspace.org/display/DSDOC5x/Upgrading+DSpace
#	A documentação completa dessa versão pode ser encontrada em
#	https://wiki.duraspace.org/display/DSDOC5x/DSpace+5.x+Documentation
#
# Versão dos software usados:
# > DSPACE:
# 	DSpace version 5.2
# 	Distributed for IBICT, Brazil
# 	Themed and adapted for SEDEPTI-BC, UFPA, PA, Brazil
# > APACHE ANT:
#	Version 1.10.1
#	Documentation available in http://ant.apache.org/manual/index.html
#	Download link http://mirror.nbtelecom.com.br/apache//ant/binaries/apache-ant-1.10.1-bin.tar.gz
# > APACHE MAVEN:
#	Version 3.5.0
#	Homepage https://maven.apache.org/index.html
#	Download link http://ftp.unicamp.br/pub/apache/maven/maven-3/3.5.0/binaries/apache-maven-3.5.0-bin.tar.gz
# > APACHE TOMCAT:
#	Version 8.5.15
#	Documentation available in http://tomcat.apache.org/tomcat-8.5-doc/index.html
#	Download link http://ftp.unicamp.br/pub/apache/tomcat/tomcat-8/v8.5.15/bin/apache-tomcat-8.5.15.tar.gz
# > JDK:
#	Version 8u131
#	Documentation available in http://www.oracle.com/technetwork/java/javase/documentation/index.html
#	Download link (you must accept the Licence Agreement) http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html
#
# Desenvolvimento:
#	Setor de Desenvolvimento de Produtos de Tecnologia da Informação (sedepti@ufpa.br)
#	Biblioteca Central da UFPA
#	Universidade Federal do Pará, Campus Belém, Brasil
# 	Author: Italo Ramon Campos (italo.ramon.campos@gmail.com)
# 	Developed by SEDEPTI - UFPA
#
# Detalhes:
#	dspace-installer.sh, version 1.5, UFPA | 2017

# =================================================
# DEFINIÇÕES DAS VARIÁVEIS GLOBAIS E IMPORTS
# =================================================
# Variáveis iniciadas com valores padrão de teste
user='dspace'
database_password='suporte'
base_dir='dspace-base'
repository_display='Repositório'
repository=''
institution='Instituição'
logo=''
dominio='localhost'
sigla='RI'

step=1
font=`pwd`
version='1.5'
dspace_version='dspace'`cat dspace/pom.xml | grep "<version>.*<\/version>" | sed "s/[[:punct:]]//g" | sed "s/[[:blank:]]//g" | sed "s/[[:alpha:]]//g"`

# Imports das bibliotecas de diálogo com o usuário
source dspace-setup/dialog.sh
source dspace-setup/verifier.sh

# =================================================
# ALTERAÇÃO DE PERMISSÕES
# =================================================
# Mudança de permissõe de acesso do diretório fonte
chmod 755 -R "$font"

# =================================================
# FORÇAR O LOGIN COMO ROOT
# =================================================
# Mudança de permissõe de acesso do diretório fonte
user_aux=`whoami`
if [ "$user_aux" != "root" ]; then
	messagebox "Identificamos que seu usuário atual é '$user_aux', e o DSpace Installer requer um usuário com permissões de 'root' para seu funcionamente correto.\nMude para o usuário 'root' e execute novamente o 'dspace-installer.sh'" "PERMISSÃO DE USUÁRIO"
	checkexit 1
fi

# =================================================
# INÍCIO DO PROCESSO DE INSTALAÇÃO
# =================================================
# Tela de boas vindas
var=$(choseboxmod "Bem-vindo ao DSpace Installer. O assistente guiará você durante o processo de instalação. Recomendamos que você leia o manual de instalação para tirar suas dúvidas e evitar problemas na configuração do seu repositório. Em caso de problemas no processo entre em contato com o suporte técnico para obter informações. Para iniciar a instalação selecione 'Instalar'. Selecione 'Sair' para cancelar.\n\n\nv$version" "BEM VINDO AO DSPACE" "Instalar" "Sair")
checkexit $var

# =================================================
# ENTRADA DE DADOS
# =================================================
# Navegação entre os passos da configuração [1-9] do arquivo build.properties
if [ "$1" != "std" ]; then
	while [ $step -gt 0 ] && [ $step -le 9 ]; do
		case $step in
			1)
				institution=$(inputboxmod "Nome completo da instituição:" "CONFIGURAÇÕES INICIAIS DSPACE" "Continuar" "Sair" "$institution")
				step=$(setstep "$institution" $step)
			;;

			2)
				sigla=$(inputboxmod "Sigla da instituição:" "CONFIGURAÇÕES INICIAIS DSPACE" "Continuar" "Voltar" "$sigla")
				step=$(setstep "$sigla" $step)
			;;

			3)
				repository=$(inputboxmod "Nome do repositório:" "CONFIGURAÇÕES INICIAIS DSPACE" "Continuar" "Voltar" "$repository_display de $institution")
				step=$(setstep "$repository" $step "r")
			;;

			4)
				logo=$(inputboxmod "Defina um logotipo para o seu repositório. Informe o caminho da imagem que você deseja usar (algo como '/home/usuario/minha_logo.png' evitando caminhos de diretórios com espaço '/home/usuario/minha pasta/minha_logo.png'). O logotipo deve estar no formato 'png'. Deixe em branco se não quiser fazer isso agora." "CONFIGURAÇÕES INICIAIS DSPACE" "Continuar" "Voltar" "$logo")
				step=$(setstep "$logo" $step)
			;;

			5)
				database_password=$(passwordboxmod "Informe a senha do banco de dados:" "CONFIGURAÇÕES INICIAIS DSPACE" "Continuar" "Voltar")
				step=$(setstep "$database_password" $step "r")
			;;

			6)
				pass_aux=$(passwordboxmod "Confirme a senha do banco de dados:" "CONFIGURAÇÕES INICIAIS DSPACE" "Confirmar" "Voltar")
				if [ "$database_password" != "$pass_aux" ]; then
					messagebox "As senhas não coincidem ('CAPSLOCK' está ligada?)." "SENHAS NÃO IDÊNTICAS"
					step=$(setstep "1" $step)
				else
					step=$(setstep "$pass_aux" $step)
				fi
			;;

			7)
				base_dir=$(inputboxmod "Nome do diretório-base de instalação do DSpace. Esse diretório será criado na raíz '/' do sistema (por isso não use '/' ou espaços).\n\nRecomendado: 'dspace-base'" "CONFIGURAÇÕES INICIAIS DSPACE" "Continuar" "Voltar" "$base_dir")
				step=$(setstep "$base_dir" $step "r")
			;;

			8)
				dominio=$(inputboxmod "Domínio do servidor. O domínio do servidor deve estar direcionado a um IP público para fucionar corretamente. Se você ainda não possui um domínio público, informe o endereço IPv4 do seu servidor. Ele deve ser fixo e tem a forma xxx.xxx.xxx.xxx (por exemplo, 192.168.97.232 ou 10.0.2.15)." "ENDEREÇO DO SERVIDOR" "Continuar" "Voltar")
				step=$(setstep "$dominio" $step "r")
			;;

			9)
				opcao=$(choseboxmod "Verifique se suas informações estão corretas:\n Instituição: $institution\n Sigla: $sigla\n Nome do Repositório: $repository\n Caminho da logo: $logo\n Senha do banco de dados: [oculto]\n Diretório-raíz do DSpace: /$base_dir\n Domínio do servidor: $dominio" "REVISÃO DOS DADOS" "Confirmar" "Começar de novo")
				if [ $opcao -eq 1 ]; then
					step=1
				else
					step=$(setstep "$opcao" $step)
				fi
			;;
		esac
	done
	# Verifica se o usuário cancelou a instalação
	if [ $step -eq 0 ]; then
		checkexit 1
	fi
	user=$(inputboxmod "O DSpace precisa de um usuário de sistema para operar. Crie agora um novo perfil de usuário padrão que o DSpace poderá usar. Não use espaços ou caracteres especiais. Informe o nome do usuário:\n\nRecomendado: 'dspace'" "NOVO USUÁRIO" "Continuar" "Cancelar instalação")
	checkexit $user
	user=$(echo $user | tr '[:upper:]' '[:lower:]') # transforma nome em lowercase
fi

# =================================================
# PROCEDIMENTOS DE PREPARAÇÃO 
# =================================================

# Ajustes no arquivo build.properties e input-forms.xml
sed -i "s/^dspace.install.dir.*/dspace.install.dir=\/$base_dir/" build.properties
checkerror $? "Arquivo build.properties não encontrado" # verifica se o arquivo de build.properties está disponível
sed -i "s/^dspace.name.*/dspace.name=$repository/" build.properties
sed -i "s/^db.username.*/db.username=$user/" build.properties
sed -i "s/^db.password.*/db.password=$database_password/" build.properties
sed -i "s/^websvc.opensearch.description.*/websvc.opensearch.description=$institution/" build.properties
sed -i "s/^dspace.hostname = .*/dspace.hostname=$dominio/" build.properties
sed -i "s/^dspace.baseUrl = .*/dspace.baseUrl=http:\/\/$dominio:8080/" build.properties
sed -i "s/^dspace.url = .*/dspace.url=\${dspace.baseUrl}\/jspui/" build.properties
sed -i "s/^db.url=jdbc:postgresql:.*/db.url=jdbc:postgresql:\/\/localhost:5432\/$dspace_version/" build.properties
sed -i "s/^       <displayed-value>Instituto.*/       <displayed-value>$institution<\/displayed-value>/" dspace/config/input-forms.xml
sed -i "s/^       <stored-value>Instituto.*/       <stored-value>$institution<\/stored-value>/" dspace/config/input-forms.xml
sed -i "s/^       <displayed-value>IBICT.*/       <displayed-value>$sigla<\/displayed-value>/" dspace/config/input-forms.xml
sed -i "s/^       <stored-value>IBICT.*/       <stored-value>$sigla<\/stored-value>/" dspace/config/input-forms.xml

# Configurando um novo grupo/usuário no sistema
addgroup $user
checkwarning $? "Não foi possível adicionar grupo de usuário. (O grupo de usuário já existe?)"
useradd -m $user -g $user
checkwarning $? "Não foi possível criar o usuário '$user'. (O usuário já existe?)"
messagebox "Informe a seguir (em linha de comando) a senha do usuário '$user'. Siga as orientações da tela."
echo "Informe a senha do usuário '$user': "
passwd $user
checkloop $? "passwd $user" #repete comando até o usuário coincidir as senhas
chsh -s /bin/bash $user

# Atualiza os Pacotes do Sistema
{
	apt-get update
} &>/dev/null &
pid=$!
showpercentsize 36380 "/var/lib/" $pid | progressbar "Atualizando lista dos pacotes do source.list do sistema, isso pode demorar..." "ATUALIZANDO LISTA DE PACOTES"

# Definição do diretório 'home' do usuário
home="/home/$user"

# Copia para a pasta do usuário os pacotes usados pelo DSpace
mkdir $home/pacotes
if [ -e packages/jdk* ]; then
	jdk_installed="1"
else
	jdk_installed="0"
fi
checkwarning $? "Problema ao criar diretório de pacotes-fonte '$home/pacotes'"
{
	if [ "$jdk_installed" = "1" ];	then
		cp packages/jdk* $home/pacotes/
	fi
	cp packages/apache-ant* $home/pacotes/
	cp packages/apache-maven* $home/pacotes/
	cp packages/apache-tomcat* $home/pacotes/
} & # executa as tarefas em segundo plano
pid=$! # recupera o pid do processo criado na linha anterior
showpercent "packages/" "$home/pacotes/" $pid | progressbar "Instalando pacotes importantes..." "INSTALANDO PACOTES"

	#Realiza as seguintes funções se não existir o arquivo binário do JDK
	if [ "$jdk_installed" = "0" ];	then
	var=$(choseboxmod "O DSpace Installer identificou que o diretório 'package' não possui o arquivo binário do JDK, por isso é necessário o download desse pacote a seguir.\n\nPara prosseguir selecione 'Continuar'. Selecione 'Sair' para cancelar." "CONFIGURANDO JDK" "Continuar" "Sair")
	checkexit $var
	percent=1
	{
		#Remove versão atual do Java JDK do Sistema
		apt-get -y remove --purge openjdk-* &>> ~/dspace-installer.log ; percent=20; echo $percent
		echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee /etc/apt/sources.list.d/webupd8team-java.list  &>> ~/dspace-installer.log ; percent=40; echo $percent
		echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list &>> ~/dspace-installer.log ; percent=60; echo $percent
		apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886 &>> ~/dspace-installer.log ; percent=80; echo $percent
		apt-get update &>> ~/dspace-installer.log ; percent=90; echo $percent
		percent=100; echo $percent
	}| progressbar "Removendo possíveis instalações do pacote JDK..." "CONFIGURANDO JDK"
	var=$(choseboxmod "Agora será feito o download e instalação do JDK compatível com a instalação do DSpace. Confirme as solicitações de Licença da Oracle a seguir.\n\nPara prosseguir selecione 'Continuar'. Selecione 'Sair' para cancelar." "CONFIGURANDO JDK" "Continuar" "Sair")
	checkexit $var
	apt-get install -y --allow-unauthenticated oracle-java8-set-default
	fi

# Extrai pacotes a serem usados pelo DSpace
percent=1
{
	#Remove versão atual do Java JDK do Sistema
	#Verifica a existência de arquivo binário do Java JDK em [dspace-fonte]/packages/
	#Caso exista segue para a utilização do mesmo para atualizar a versão
	if [ "$jdk_installed" = "1" ];	then
		apt-get -y remove --purge openjdk-* &>> ~/dspace-installer.log; percent=$((percent+7)); echo $percent
		tar zxf $home/pacotes/jdk* -C /opt/; percent=$((percent+7)); echo $percent
		mv /opt/jdk* /opt/jdk; percent=$((percent+7)); echo $percent
		update-alternatives --install /usr/bin/java java /opt/jdk/bin/java 100; percent=$((percent+7)); echo $percent
		update-alternatives --install /usr/bin/javac javac /opt/jdk/bin/javac 100; percent=$((percent+7)); echo $percent
	fi
	
	tar zxf $home/pacotes/apache-ant* -C $home; percent=$((percent+7)); echo $percent
	mv $home/apache-ant* $home/apache-ant; percent=$((percent+7)); echo $percent
	tar zxf $home/pacotes/apache-maven* -C $home; percent=$((percent+7)); echo $percent
	mv $home/apache-maven* $home/apache-maven; percent=$((percent+7)); echo $percent
	tar zxf $home/pacotes/apache-tomcat* -C $home; percent=$((percent+7)); echo $percent
	mv $home/apache-tomcat* $home/apache-tomcat; percent=$((percent+7)); echo $percent

	# Cria diretórios e altera permissões
	mkdir /$base_dir
	checkwarning $? "Não foi possível criar o diretório base '/$base_dir'. (Já existe alguma pasta com esse nome?)"; percent=$((percent+7)); echo $percent
	changeown "/$base_dir" $user; percent=$((percent+7)); echo $percent
	changeown $home $user; percent=$((percent+7)); echo $percent
	percent=100; echo $percent
} | progressbar "Expandindo arquivos do DSpace..." "EXPANDINDO ARQUIVOS"

# Instala o SGBD no sistema [PostgreSQL]
{
	apt-get install postgresql -y
} &>> ~/dspace-installer.log &
pid=$!
showpercentsize 36380 "/var/lib/" $pid | progressbar "Instalando o sistema gerenciador de banco de dados..." "INSTALANDO SGBD"

# Configura os arquivos do postgres para localhost
version=`ls /etc/postgresql`
cd /etc/postgresql/$version
cd main/
sed -i "s/^#listen_addresses = 'localhost'.*/listen_addresses = 'localhost'  	# what IP address(es) to listen on;/" postgresql.conf
checkerror $? "Não foi possível encontrar os arquivos de configuração do PostgreSQL (/etc/postgresql)"
echo "host	all	all	127.0.0.1		255.255.255.0	md5" >> pg_hba.conf

# =================================================
# PROCESSOS OPERADOS POR USUÁRIO
# =================================================

cd "$font"

# Cria usuário de banco de dados
#messagebox "Configure a seguir a senha do banco de dados (em linha de comando). Tenha cuidado de usar exatamente a mesma senha de banco de dados fornecida nas configurações iniciais do DSpace, caso contrário o repositório não poderá acessar o banco de dados. Siga as instruções da tela." "CONFIGURAR SENHA DE BANCO DE DADOS"
su postgres -c "dspace-setup/dspace-dbuser.sh $user $database_password" -s /bin/bash postgres
checkerror $? "Erro ao criar usuário do banco de dados"

# Cria o banco de dados
su $user -c "createdb -E UNICODE $dspace_version" -s /bin/bash $user
checkerror $? "Erro ao criar banco de dados"

# Copia os arquivos de instalação para 'home' do usuário DSpace
{
	su $user -c "dspace-setup/dspace-source.sh $home $dspace_version" -s /bin/bash $user
} &>/dev/null &
pid=$!
showpercent "$font" "$home" $pid | progressbar "Copiando arquivos de instalação..." "COPIANDO ARQUIVOS"; getfail

# Compila o código-fonte do DSpace
{
	su $user -c "dspace-setup/dspace-compiler.sh $home $dspace_version" -s /bin/bash $user
} &>/dev/null &
pid=$!
showpercentsize 3468348 "$home/$dspace_version" $pid | progressbar "Compilando arquivos do DSpace. Por favor, certifique-se de estar conectado ininterruptamente à internet. Este processo demora em média 25 minutos, mas pode variar dependendo da velocidade de rede.\nCompilando..." "INSTALANDO DSPACE"; getfail

# Instala os arquivos-base do DSpace
{
	su $user -c "dspace-setup/dspace-install.sh $home $dspace_version" -s /bin/bash $user
} &>/dev/null &
pid=$!
showpercentsize 796772 "/$base_dir" $pid | progressbar "Instalando arquivos do DSpace. Este processo deve demorar alguns minutos.\nInstalando..." "INSTALANDO DSPACE"; getfail

# Cria e configura um perfil de administrador (master) para o DSpace
messagebox "Configure a seguir o perfil de administrador do DSpace (em linha de comando). Esse perfil será o superusuário do seu repositório, por isso tenha certeza de configurá-lo corretamente para evitar problemas de funcionalidade. Siga as orientações da tela (em inglês)." "CRIAR ADMINISTRADOR"
echo "Aguarde..."
su $user -c "/$base_dir/bin/dspace create-administrator" -s /bin/bash $user
checkwarning $? "Problema ao configurar o perfil de administrador do Dspace"

# Configura os serviços web da aplicação
if [ "$logo" != "" ]; then
	changeown "$logo" $user
fi
{
	su $user -c "dspace-setup/dspace-webservice.sh '$base_dir' $home $dspace_version '$logo'" -s /bin/bash $user
} &>/dev/null &
pid=$!
showpercent "/$base_dir/webapps" "$home/apache-tomcat/webapps" $pid | progressbar "Configurando arquivos da aplicação web do DSpace..." "ÚLTIMAS CONFIGURAÇÕES"; getfail

cd "$font"

# =================================================
# CONFIGURAÇÕES DE SERVIÇO WEB
# =================================================

# Configura Apache Tomcat
percent=1
{
	sed -i 's/^               redirectPort="8443".*/               redirectPort="8443"	URIEncoding="UTF-8" \/>/' $home/apache-tomcat/conf/server.xml
	checkwarning $? "Não foi possível alterar o arquivo de formatação UTF-8 do Apache Tomcat"; percent=$((percent+12)); echo $percent
	cp dspace-setup/tomcat /etc/init.d/
	checkwarning $? "Problemas ao copiar script de inicialização do Apache Tomcat"; percent=$((percent+12)); echo $percent
	cd /etc/init.d/; percent=$((percent+12)); echo $percent
	sed -i "s/^user='dspace'.*/user='$user'/" tomcat; percent=$((percent+12)); echo $percent
	chmod 775 tomcat; percent=$((percent+12)); echo $percent
	update-rc.d tomcat defaults; percent=$((percent+12)); echo $percent
	touch $home/apache-tomcat/logs/actions.log; percent=$((percent+12)); echo $percent
	sh tomcat start; percent=$((percent+12)); echo $percent
	percent=100; echo $percent
} | progressbar "Configurando Apache Tomcat..." "CONFIGURANDO SERVIÇO DE APLICAÇÃO WEB"

# Remove arquivos de instalação
percent=1
{
	cd $home/$dspace_version; percent=$((percent+50)); echo $percent
	rm "$font" -Rf; percent=$((percent+50)); echo $percent
} | progressbar "Removendo arquivos temporários..." "LIMPANDO"

messagebox "A instalação foi concluída com êxito. Por favor, salve seus trabalhos e reinicie a máquina. Em seguida acesse $dominio:8080/jspui para ver seu repositório." "INSTALAÇÃO FINALIZADA"

# =================================================
# FIM DO PROCESSO DE INSTALAÇÃO
# =================================================
