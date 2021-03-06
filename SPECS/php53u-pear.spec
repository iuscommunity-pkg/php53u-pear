
%global peardir %{_datadir}/pear

%global xmlrpcver 1.5.1
%global getoptver 1.2.3
%global arctarver 1.3.3
%global structver 1.0.2
%global xmlutil   1.2.1

%define php_base php53u
%define basever 1.9
%define real_name php-pear
%define name %{php_base}-pear
Summary: PHP Extension and Application Repository framework
Name: %{name}
Version: 1.9.4
Release: 3.ius%{?dist}
Epoch: 1
License: PHP
Group: Development/Languages
URL: http://pear.php.net/package/PEAR
Source0: http://download.pear.php.net/package/PEAR-%{version}.tgz
# wget http://cvs.php.net/viewvc.cgi/pear-core/install-pear.php?revision=1.39 -O install-pear.php
Source1: install-pear.php
Source2: relocate.php
Source3: strip.php
Source4: LICENSE
Source10: pear.sh
Source11: pecl.sh
Source12: peardev.sh
Source13: macros.pear
Source20: http://pear.php.net/get/XML_RPC-%{xmlrpcver}.tgz
Source21: http://pear.php.net/get/Archive_Tar-%{arctarver}.tgz
Source22: http://pear.php.net/get/Console_Getopt-%{getoptver}.tgz
Source23: http://pear.php.net/get/Structures_Graph-%{structver}.tgz
Source24: http://pear.php.net/get/XML_Util-%{xmlutil}.tgz

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: %{php_base}-cli, %{php_base}-xml, gnupg
Provides: php-pear(Console_Getopt) = %{getoptver}
Provides: php-pear(Archive_Tar) = %{arctarver}
Provides: php-pear(PEAR) = %{version}
Provides: php-pear(Structures_Graph) = %{structver}
Provides: php-pear(XML_RPC) = %{xmlrpcver}
Provides: php-pear(XML_Util) = %{xmlutil}
Provides: %{php_base}-pear(Console_Getopt) = %{getoptver}
Provides: %{php_base}-pear(Archive_Tar) = %{arctarver}
Provides: %{php_base}-pear(PEAR) = %{version}
Provides: %{php_base}-pear(Structures_Graph) = %{structver}
Provides: %{php_base}-pear(XML_RPC) = %{xmlrpcver}
Provides: %{php_base}-pear(XML_Util) = %{xmlutil}
Provides: %{php_base}-pear-XML-Util = %{xmlutil}-%{release}
Requires: %{php_base}-cli

# IUS Stuff
Provides: %{real_name} = %{version}
Conflicts: %{real_name} < %{basever}

# FIX ME: Should be removed before/after RHEL 5.6 is out
# See: https://bugs.launchpad.net/ius/+bug/691755


%description
PEAR is a framework and distribution system for reusable PHP
components.  This package contains the basic PEAR components.

%prep
%setup -cT -n %{real_name}-%{version}

# Create a usable PEAR directory (used by install-pear.php)
for archive in %{SOURCE0} %{SOURCE21} %{SOURCE22} %{SOURCE23} %{SOURCE24}
do
    tar xzf  $archive --strip-components 1 || tar xzf  $archive --strip-path 1
done
tar xzf %{SOURCE24} package.xml
mv package.xml XML_Util.xml

# apply patches on used PEAR during install
# -- no patch

%build
# This is an empty build section.

%install
rm -rf $RPM_BUILD_ROOT

export PHP_PEAR_SYSCONF_DIR=%{_sysconfdir}
export PHP_PEAR_SIG_KEYDIR=%{_sysconfdir}/pearkeys
export PHP_PEAR_SIG_BIN=%{_bindir}/gpg
export PHP_PEAR_INSTALL_DIR=%{peardir}

# 1.4.11 tries to write to the cache directory during installation
# so it's not possible to set a sane default via the environment.
# The ${PWD} bit will be stripped via relocate.php later.
export PHP_PEAR_CACHE_DIR=${PWD}%{_localstatedir}/cache/php-pear
export PHP_PEAR_TEMP_DIR=/var/tmp

install -d $RPM_BUILD_ROOT%{peardir} \
           $RPM_BUILD_ROOT%{_localstatedir}/cache/php-pear \
           $RPM_BUILD_ROOT%{_localstatedir}/www/html \
           $RPM_BUILD_ROOT%{peardir}/.pkgxml \
           $RPM_BUILD_ROOT%{_sysconfdir}/rpm \
           $RPM_BUILD_ROOT%{_sysconfdir}/pear

export INSTALL_ROOT=$RPM_BUILD_ROOT

%{_bindir}/php -n -dmemory_limit=32M -dshort_open_tag=0 -dsafe_mode=0 \
         -derror_reporting=E_ALL -ddetect_unicode=0 \
      %{SOURCE1} -d %{peardir} \
                 -c %{_sysconfdir}/pear \
                 -b %{_bindir} \
                 -w %{_localstatedir}/www/html \
                 %{SOURCE0} %{SOURCE21} %{SOURCE22} %{SOURCE23} %{SOURCE24} %{SOURCE20}

# Replace /usr/bin/* with simple scripts:
install -m 755 %{SOURCE10} $RPM_BUILD_ROOT%{_bindir}/pear
install -m 755 %{SOURCE11} $RPM_BUILD_ROOT%{_bindir}/pecl
install -m 755 %{SOURCE12} $RPM_BUILD_ROOT%{_bindir}/peardev

# Sanitize the pear.conf
%{_bindir}/php -n %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf $RPM_BUILD_ROOT | 
  %{_bindir}/php -n %{SOURCE2} php://stdin $PWD > new-pear.conf
%{_bindir}/php -n %{SOURCE3} new-pear.conf ext_dir |
  %{_bindir}/php -n %{SOURCE3} php://stdin http_proxy > $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf

%{_bindir}/php -r "print_r(unserialize(substr(file_get_contents('$RPM_BUILD_ROOT%{_sysconfdir}/pear.conf'),17)));"

install -m 644 -c %{SOURCE4} LICENSE

install -m 644 -c %{SOURCE13} \
           $RPM_BUILD_ROOT%{_sysconfdir}/rpm/macros.pear     

# apply patches on installed PEAR tree
pushd $RPM_BUILD_ROOT%{peardir} 
# -- no patch
popd

# Why this file here ?
rm -rf $RPM_BUILD_ROOT/.depdb* $RPM_BUILD_ROOT/.lock $RPM_BUILD_ROOT/.channels $RPM_BUILD_ROOT/.filemap

# Need for re-registrying XML_Util
install -m 644 XML_Util.xml $RPM_BUILD_ROOT%{peardir}/.pkgxml/


%check
# Check that no bogus paths are left in the configuration, or in
# the generated registry files.
grep $RPM_BUILD_ROOT $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf && exit 1
grep %{_libdir} $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf && exit 1
grep '"/tmp"' $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf && exit 1
grep /usr/local $RPM_BUILD_ROOT%{_sysconfdir}/pear.conf && exit 1
grep -rl $RPM_BUILD_ROOT $RPM_BUILD_ROOT && exit 1


%clean
rm -rf $RPM_BUILD_ROOT
rm new-pear.conf


%triggerpostun -- php-pear-XML-Util
# re-register extension unregistered during postun of obsoleted php-pear-XML-Util
%{_bindir}/pear install --nodeps --soft --force --register-only %{pear_xmldir}/XML_Util.xml >/dev/null || :


%files
%defattr(-,root,root,-)
%{peardir}
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/pear.conf
%config %{_sysconfdir}/rpm/macros.pear
%dir %{_localstatedir}/cache/php-pear
%dir %{_localstatedir}/www/html
%dir %{_sysconfdir}/pear
%doc LICENSE README


%changelog
* Fri Aug 19 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> -  - 1:1.9.4-3.ius
- Rebuilding

* Fri Aug 12 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> -  - 1:1.9.4-2.ius
- Rebuilding with EL6 support

* Thu Jul 07 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> -  - 1:1.9.4-1.ius
- Latest sources from upstream

* Mon Jun 06 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> -  - 1:1.9.3-1.ius
- Latest sources from upstream

* Mon Mar 21 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> -  - 1:1.9.2-1.ius
- Latest sources from upstream
- PEAR installer symlink vulnerability
  http://pear.php.net/advisory-20110228.txt

* Tue Feb 01 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 1:1.8.1-7.ius
- Removed Obsoletes: php53*

* Fri Dec 17 2010 BJ Dierkes <wdierkes@rackspace.com> - 1:1.8.1-6.ius
- Renaming to php53u-pear.  Resolves LP#691755
  Obsoletes: php53-pear

* Thu Sep 09 2010 BJ Dierkes <wdierkes@rackspace.com> - 1:1.8.1-5.ius
- No longer Obsoletes: php-pear18

* Tue Jun 15 2010 BJ Dierkes <wdierkes@rackspace.com> - 1:1.8.1-4.ius
- Rebuilding for 5.x (RHEL EUS) repos

* Wed Feb 10 2010 BJ Dierkes <wdierkes@rackspace.com> - 1:1.8.1-3.ius
- Rebuilding for php53
- Obsoletes php-pear18

* Thu Dec 17 2009 BJ Dierkes <wdierkes@rackspace.com> - 1:1.8.1-2.ius
- Repackaging for php52 specifically to resolve dep issues. 

* Fri Jul 31 2009 BJ Dierkes <wdierkes@rackspace.com> - 1:1.8.1-1.ius 
- Repackaging for IUS
- Changed name to php-pear18

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat May 30 2009 Remi Collet <Fedora@FamilleCollet.com> 1:1.8.1-1
- update to 1.8.1
- Update install-pear.php script (1.39)
- add XML_Util

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.7.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun May 18 2008 Remi Collet <Fedora@FamilleCollet.com> 1:1.7.2-2
- revert to install-pear.php script 1.31 (for cfg_dir)

* Sun May 18 2008 Remi Collet <Fedora@FamilleCollet.com> 1:1.7.2-1
- update to 1.7.2
- Update install-pear.php script (1.32)

* Tue Mar 11 2008 Tim Jackson <rpm@timj.co.uk> 1:1.7.1-2
- Set cfg_dir to be %%{_sysconfdir}/pear (and own it)
- Update install-pear.php script
- Add %%pear_cfgdir and %%pear_wwwdir macros

* Sun Feb  3 2008 Remi Collet <Fedora@FamilleCollet.com> 1:1.7.1-1
- update to 1.7.1

* Fri Feb  1 2008 Remi Collet <Fedora@FamilleCollet.com> 1:1.7.0-1
- update to 1.7.0

* Thu Oct  4 2007 Joe Orton <jorton@redhat.com> 1:1.6.2-2
- require php-cli not php

* Sun Sep  9 2007 Remi Collet <Fedora@FamilleCollet.com> 1:1.6.2-1
- update to 1.6.2
- remove patches merged upstream
- Fix : "pear install" hangs on non default channel (#283401)

* Tue Aug 21 2007 Joe Orton <jorton@redhat.com> 1:1.6.1-2
- fix License

* Thu Jul 19 2007 Remi Collet <Fedora@FamilleCollet.com> 1:1.6.1-1
- update to PEAR-1.6.1 and Console_Getopt-1.2.3

* Thu Jul 19 2007 Remi Collet <Fedora@FamilleCollet.com> 1:1.5.4-5
- new SPEC using install-pear.php instead of install-pear-nozlib-1.5.4.phar

* Mon Jul 16 2007 Remi Collet <Fedora@FamilleCollet.com> 1:1.5.4-4
- update macros.pear (without define)

* Mon Jul 16 2007 Joe Orton <jorton@redhat.com> 1:1.5.4-3
- add pecl_{un,}install macros to macros.pear (from Remi)

* Fri May 11 2007 Joe Orton <jorton@redhat.com> 1:1.5.4-2
- update to 1.5.4

* Tue Mar  6 2007 Joe Orton <jorton@redhat.com> 1:1.5.0-3
- add redundant build section (#226295)
- BR php-cli not php (#226295)

* Mon Feb 19 2007 Joe Orton <jorton@redhat.com> 1:1.5.0-2
- update builtin module provides (Remi Collet, #226295)
- drop patch 0

* Thu Feb 15 2007 Joe Orton <jorton@redhat.com> 1:1.5.0-1
- update to 1.5.0

* Mon Feb  5 2007 Joe Orton <jorton@redhat.com> 1:1.4.11-4
- fix Group, mark pear.conf noreplace (#226295)

* Mon Feb  5 2007 Joe Orton <jorton@redhat.com> 1:1.4.11-3
- use BuildArch not BuildArchitectures (#226925)
- fix to use preferred BuildRoot (#226925)
- strip more buildroot-relative paths from *.reg
- force correct gpg path in default pear.conf

* Thu Jan  4 2007 Joe Orton <jorton@redhat.com> 1:1.4.11-2
- update to 1.4.11

* Fri Jul 14 2006 Joe Orton <jorton@redhat.com> 1:1.4.9-4
- update to XML_RPC-1.5.0
- really package macros.pear

* Thu Jul 13 2006 Joe Orton <jorton@redhat.com> 1:1.4.9-3
- require php-cli
- add /etc/rpm/macros.pear (Christopher Stone)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1:1.4.9-2.1
- rebuild

* Mon May  8 2006 Joe Orton <jorton@redhat.com> 1:1.4.9-2
- update to 1.4.9 (thanks to Remi Collet, #183359)
- package /usr/share/pear/.pkgxml (#190252)
- update to XML_RPC-1.4.8
- bundle the v3.0 LICENSE file

* Tue Feb 28 2006 Joe Orton <jorton@redhat.com> 1:1.4.6-2
- set cache_dir directory, own /var/cache/php-pear

* Mon Jan 30 2006 Joe Orton <jorton@redhat.com> 1:1.4.6-1
- update to 1.4.6
- require php >= 5.1.0 (#178821)

* Fri Dec 30 2005 Tim Jackson <tim@timj.co.uk> 1:1.4.5-6
- Patches to fix "pear makerpm"

* Wed Dec 14 2005 Joe Orton <jorton@redhat.com> 1:1.4.5-5
- set default sig_keydir to /etc/pearkeys
- remove ext_dir setting from /etc/pear.conf (#175673)

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Tue Dec  6 2005 Joe Orton <jorton@redhat.com> 1:1.4.5-4
- fix virtual provide for PEAR package (#175074)

* Sun Dec  4 2005 Joe Orton <jorton@redhat.com> 1:1.4.5-3
- fix /usr/bin/{pecl,peardev} (#174882)

* Thu Dec  1 2005 Joe Orton <jorton@redhat.com> 1:1.4.5-2
- add virtual provides (#173806) 

* Wed Nov 23 2005 Joe Orton <jorton@redhat.com> 1.4.5-1
- initial build (Epoch: 1 to allow upgrade from php-pear-5.x)
