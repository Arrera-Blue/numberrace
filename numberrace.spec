Name:           numberrace
Version:        3.1.1
Release:        1%{?dist}
Summary:        Adaptive educational math game for children (La Course aux Nombres)
Summary(fr):    Jeu éducatif de mathématiques pour enfants (La Course aux Nombres)

License:        GPL-2.0-only
URL:            http://thenumberrace.com
BuildArch:      noarch

Source0:        numberrace-installer-%{version}-fr.jar
Source1:        extract-izpack.py
Source2:        numberrace.desktop
Source3:        numberrace.sh
Source4:        org.unicog.numberrace.metainfo.xml
Source5:        make-icons.py

BuildRequires:  appstream
BuildRequires:  desktop-file-utils
BuildRequires:  python3
BuildRequires:  python3-pillow

Requires:       hicolor-icon-theme
Requires:       java >= 1:1.8.0

%description
The Number Race (La Course aux Nombres) is an adaptive educational game
designed by the INSERM-CEA Cognitive Neuroimaging Unit for children aged 4 to 8.
It teaches and reinforces basic numerical and arithmetic concepts and supports
remediation of dyscalculia.

%description -l fr
La Course aux Nombres est un jeu éducatif adaptatif conçu par l'Unité
INSERM-CEA de Neuroimagerie Cognitive pour les enfants de 4 à 8 ans.
Il permet de découvrir et de pratiquer les concepts numériques et arithmétiques
de base et d'aider à la remédiation de la dyscalculie.

%prep
%setup -q -c -T
python3 %{SOURCE1} %{SOURCE0} .
mv README README.html
rm -f numberrace.exe numberrace-uninstaller.exe start.sh

%build
# Pre-built Java archives extracted from upstream installer

%install
install -d %{buildroot}%{_datadir}/%{name}/lib/langs
install -m 0644 lib/*.jar %{buildroot}%{_datadir}/%{name}/lib/
install -m 0644 lib/langs/*.jar %{buildroot}%{_datadir}/%{name}/lib/langs/

install -D -m 0755 %{SOURCE3} %{buildroot}%{_bindir}/%{name}
python3 %{SOURCE5} images/numberraceIcon64x64.png \
    %{buildroot}%{_datadir}/icons/hicolor
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE2}
install -D -m 0644 %{SOURCE4} \
    %{buildroot}%{_datadir}/metainfo/org.unicog.numberrace.metainfo.xml

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstreamcli validate --no-net --explain \
    %{buildroot}%{_datadir}/metainfo/org.unicog.numberrace.metainfo.xml

%files
%license gpl-2.0.html
%doc README.html
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/metainfo/org.unicog.numberrace.metainfo.xml

%changelog
* Sun Nov 22 2026 Packager <packager@localhost> - 3.1.1-2
- Generate rounded padded hicolor icons (48x48 to 256x256) for GNOME integration
- Add windowed-mode desktop action

* Sun Nov 22 2026 Packager <packager@localhost> - 3.1.1-1
- Initial Fedora RPM package for The Number Race (French edition)
