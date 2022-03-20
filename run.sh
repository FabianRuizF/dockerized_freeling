docker build . -t localfreeling
docker kill freeling_container
docker rm freeling_container
docker run --volume=/home/fruiz/testing/freeling_files:/root/freeling_files --volume=/home/fruiz/testing/it.cfg:/usr/local/share/freeling/config/it.cfg --name freeling_container -d -i -t localfreeling:latest
