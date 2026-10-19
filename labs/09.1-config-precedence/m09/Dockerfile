# syntax=docker/dockerfile:1
FROM alpine:3.24
ARG BUILD_NOTE=default-note
ENV GREETING="from image" \
    LOG_LEVEL=info
RUN echo "build note was: $BUILD_NOTE" > /build-note.txt
CMD ["sh", "-c", "echo GREETING=$GREETING LOG_LEVEL=$LOG_LEVEL BUILD_NOTE=${BUILD_NOTE:-unset}; cat /build-note.txt"]
