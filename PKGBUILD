# Maintainer: Mr Green

pkgname=beerfetch
pkgver=0.2
pkgrel=1
pkgdesc="A very basic bash version of neofetch"
arch=('any')
url="https://github.com/mrgreen3/beerfetch"
license=('GPL')
depends=('bash' 'pacman-contrib' 'xorg-xprop')
source=("https://github.com/mrgreen3/beerfetch/archive/refs/heads/main.tar.gz")
sha256sums=('da45d2fbf2bca3a740f5f45a6162a9dafa209c7ddb9bd03a53cc03e4c4c879ad')

build() {
  cd "$srcdir/beerfetch-main"
  # No specific build instructions needed for a bash script
}

package() {
  cd "$srcdir/beerfetch-main"
  install -Dm755 beerfetch "$pkgdir/usr/bin/beerfetch"
}

