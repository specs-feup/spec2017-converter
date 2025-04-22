import installation
import unspec
import check_unspec
import os



if __name__ == "__main__":
    iso_path = "cpu2017-1_0_5.iso"
    output_dir = "cpu2017"
    if os.path.isdir(output_dir):
        print("Folder exists!")
    else:
        installation.main(iso_path, output_dir)
    unspec.main()
    check_unspec.main()
