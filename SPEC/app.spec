%global git_owner Yong
%global git_name APP
%global project_id 875
%global git_commit 77fa51fe7b70449cdcffbfe6f3e25adfcbb5d4d4
%global gitlab_token icSipdnzstRJf__FaFEr
%define name       app
%{!?revision:%define revision 1}
%define version    5.0.3
%define __jar_repack %{nil}

%define app_home /opt/apps/app
%define app_user app
%define app_group app

Summary:        Exaple APP
License:        Nuance Proprietary
Name:           %{name}
Version:        %{version}
Release:        %{revision}
Source:         %{git_name}.tar.gz
Prefix:         /usr
Group:          Development/Tools
Requires:       app-etc cronie
BuildArch:      noarch

%description
Test App

%prep
curl --header "PRIVATE-TOKEN: %{gitlab_token}" https://git.labs.hosting.app.net/api/v4/projects/%{project_id}/repository/archive.tar.gz?sha=%{git_commit} -o ../SOURCES/%{git_name}.tar.gz
%autosetup -n %{git_name}-%{git_commit}-%{git_commit}

%install
export JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8
mvn -Dproject.build.sourceEncoding=UTF-8 clean
mvn -Dproject.build.sourceEncoding=UTF-8 clean package
mkdir -p %{buildroot}%{app_home}/lib %{buildroot}%{app_home}/app_cmd_app/cron
mkdir -p %{buildroot}/etc/cron.d %{buildroot}%{app_home}/audios
cp -lR  %{_builddir}/%{git_name}-%{git_commit}-%{git_commit}/app_cmd_app/* %{buildroot}%{app_home}/app_cmd_app/
rm -rf %{buildroot}%{app_home}/app_cmd_app/data/
cp -l %{_builddir}/%{git_name}-%{git_commit}-%{git_commit}/app_cmd_app/cron/app_db_cleanup.cron %{buildroot}/etc/cron.d/app_db_cleanup
cp -l %{_builddir}/%{git_name}-%{git_commit}-%{git_commit}/target/%{git_name}-%{version}-SNAPSHOT-jar-with-dependencies.jar %{buildroot}%{app_home}/lib/app-fat.jar
cp -lR  %{_builddir}/%{git_name}-%{git_commit}-%{git_commit}/audios/* %{buildroot}%{app_home}/audios/
mkdir -p %{buildroot}/var/log/app/app_web

echo %{git_commit} > %{buildroot}%{app_home}/commit.txt

# drop the startup script
install -d -m 755 %{buildroot}%{app_home}/bin
install    -m 755 %{_builddir}/%{git_name}-%{git_commit}-%{git_commit}/src/main/shell/startup.sh %{buildroot}%{app_home}/bin

# Drop environment file
install -d -m 755 %{buildroot}%{_sysconfdir}
install -d -m 755 %{buildroot}%{_sysconfdir}/sysconfig
install    -m 644 %{_topdir}/SOURCES/app_env %{buildroot}/%{_sysconfdir}/sysconfig/app_env

# Drop systemd script
install -d -m 755 %{buildroot}/usr/lib/systemd/system
install    -m 644 %{_topdir}/SOURCES/redhat/app.systemd %{buildroot}/usr/lib/systemd/system/app.service

# Create /var/lib/app
install -d -m 755 %{buildroot}/var/lib/app

%pre
getent group %{app_group} >/dev/null || groupadd -r %{app_group}
getent passwd %{app_user} >/dev/null || /usr/sbin/useradd --comment "APP Daemon User" --shell /bin/bash -M -r -g %{app_group} --home %{app_home} %{app_user}


%post
chown -R %{app_user}:%{app_group} /var/log/app/app_web
rm -f /tmp/app_db_cleanup.log
systemctl daemon-reload

%files
%defattr(-,root,root)
%{app_home}
/etc/cron.d/app_db_cleanup
%config(noreplace) %{_sysconfdir}/sysconfig/app_env
%defattr(-,%{app_user},%{app_group})
%attr(755,%{app_user},%{app_group})
/var/log/app/app_web
/var/lib/app
%defattr(-,root,root)
/usr/lib/systemd/system/app.service
