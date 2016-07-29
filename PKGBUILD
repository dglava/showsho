pkgname=showsho-git
pkgver=r57.2fd4e37
pkgrel=1
pkgdesc="Keep track of your shows and download them easily"
url="https://github.com/dglava/showsho"
arch=('any')
license=('GPL3')
depends=('python')
makedepends=('git')
source=('git+https://github.com/dglava/showsho.git')
sha1sums=('SKIP')

pkgver() {
  cd "$srcdir/${pkgname%-git}"
  printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package() {
  cd "$srcdir/${pkgname%-git}"
  python setup.py install --root="$pkgdir"
}
