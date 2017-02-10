# Fedora spec file for php-smbclient
# with SCL compatibility removed, from
#
# remirepo spec file for php-smbclient
#
# Copyright (c) 2015 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#

%global pecl_name  smbclient
%global with_zts   0%{?__ztsphp:1}
%global ini_name   40-%{pecl_name}.ini
# Test suite requires a Samba server and configuration file
%global with_tests 0%{?_with_tests:1}

Name:           php-smbclient
Version:        0.8.0
Release:        3%{?dist}
Summary:        PHP wrapper for libsmbclient

Group:          Development/Languages
License:        BSD
URL:            https://github.com/eduardok/libsmbclient-php
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}%{?prever}.tgz
%if %{with_tests}
Source2:        %{pecl_name}-phpunit.xml
%endif

BuildRequires:  php-devel
BuildRequires:  php-pear
BuildRequires:  libsmbclient-devel > 3.6
%if %{with_tests}
BuildRequires:  php-composer(phpunit/phpunit)
BuildRequires:  samba
%endif

Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}

# Renamed (and "php -m" reports both smbclient and libsmbclient)
Obsoletes:      php-libsmbclient         < 0.8.0-0.2
Provides:       php-libsmbclient         = %{version}-%{release}
Provides:       php-libsmbclient%{?_isa} = %{version}-%{release}
# PECL
Provides:       php-pecl-%{pecl_name}          = %{version}-%{release}
Provides:       php-pecl-%{pecl_name}%{?_isa}  = %{version}-%{release}
Provides:       php-pecl(%{pecl_name})         = %{version}
Provides:       php-pecl(%{pecl_name})%{?_isa} = %{version}


%description
%{pecl_name} is a PHP extension that uses Samba's libsmbclient
library to provide Samba related functions and 'smb' streams
to PHP programs.


%prep
%setup -q -c
mv %{pecl_name}-%{version}%{?prever} NTS

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    -e '/LICENSE/s/role="doc"/role="src"/' \
    -i package.xml

cd NTS
# Check extension version
ver=$(sed -n '/define PHP_SMBCLIENT_VERSION/{s/.* "//;s/".*$//;p}' php_smbclient.h)
if test "$ver" != "%{version}%{?prever}"; then
   : Error: Upstream VERSION version is ${ver}, expecting %{version}%{?prever}.
   exit 1
fi
cd ..

cat  << 'EOF' | tee %{ini_name}
; Enable %{summary} extension module
extension=%{pecl_name}.so
EOF

%if %{with_zts}
# Duplicate source tree for NTS / ZTS build
cp -pr NTS ZTS
%endif


%build
cd NTS
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
%configure --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
%endif


%install
make -C NTS install INSTALL_ROOT=%{buildroot}

# install configuration
install -Dpm 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

%if %{with_zts}
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -Dpm 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
: Minimal load test for NTS extension
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

%if %{with_zts}
: Minimal load test for NTS extension
%{__ztsphp} --no-php-ini \
    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}
%endif

%if %{with_tests}
: Upstream test suite for NTS extension
cd NTS
cp %{SOURCE2} phpunit.xml

%{__php} \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    %{_bindir}/phpunit --verbose
%endif


%files
%license NTS/LICENSE
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Mon Nov 14 2016 Remi Collet <remi@fedoraproject.org> - 0.8.0-3
- rebuild for https://fedoraproject.org/wiki/Changes/php71

* Mon Jun 27 2016 Remi Collet <remi@fedoraproject.org> - 0.8.0-2
- rebuild for https://fedoraproject.org/wiki/Changes/php70

* Wed Mar  2 2016 Remi Collet <remi@fedoraproject.org> - 0.8.0-1
- update to 0.8.0 (stable, no change)
- drop scriptlets (replaced by file triggers in php-pear)
- cleanup

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.0-0.5.RC1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Dec  8 2015 Remi Collet <remi@fedoraproject.org> - 0.8.0-0.4.RC1
- now available on PECL
- use sources from pecl
- add virtual provides
- add scriptlets for pecl registry (un)registration

* Thu Sep 17 2015 Remi Collet <remi@fedoraproject.org> - 0.8.0-0.3.rc1
- cleanup SCL compatibility for Fedora

* Wed Sep 16 2015 Remi Collet <rcollet@redhat.com> - 0.8.0-0.2.rc1
- update to 0.8.0-rc1
- rename from php-libsmbclient to php-smbclient
  https://github.com/eduardok/libsmbclient-php/pull/26

* Thu Sep  3 2015 Remi Collet <rcollet@redhat.com> - 0.8.0-0.1.20150909gita65127d
- update to 0.8.0-dev
- https://github.com/eduardok/libsmbclient-php/pull/20 streams support
- https://github.com/eduardok/libsmbclient-php/pull/23 PHP 7

* Thu Sep  3 2015 Remi Collet <rcollet@redhat.com> - 0.7.0-1
- Update to 0.7.0
- drop patches merged upstream
- license is now BSD

* Wed Sep  2 2015 Remi Collet <rcollet@redhat.com> - 0.6.1-1
- Initial packaging of 0.6.1
- open https://github.com/eduardok/libsmbclient-php/pull/17
  test suite configuration
- open https://github.com/eduardok/libsmbclient-php/pull/18
  add reflection and improve phpinfo
- open https://github.com/eduardok/libsmbclient-php/issues/19
  missing license file
