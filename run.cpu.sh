docker build . -f Dockerfile.cpu -t roop-unleashed-cpu
docker run -it --rm \
    -v ~/ML/media/:/roop-unleashed/media/ \
    -v ~/ML/models:/roop-unleashed/models \
    -v ~/ML/models/.insightface/:/root/.insightface/ \
    -v ~/ML/models/.opennsfw2/:/root/.opennsfw2/ \
    roop-unleashed-cpu \
    -s ./media/michelle-obama.jpg -t ./media/serena-red.jpg -o ./media/output__.jpg