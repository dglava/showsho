from distutils.core import setup

setup(
    name = "showsho",
    version = "0.1.0",
    author = "Dino Duratović",
    author_email = "dinomol@mail.com",
    description = "Keep track of your shows and download them easily",
    license = "GNU GPLv3",

    packages = ["showsho"],
    scripts = ["bin/showsho"],
    )
