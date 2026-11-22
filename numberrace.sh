#!/bin/sh
exec java ${JAVA_OPTS:-} -jar /usr/share/numberrace/lib/numberrace-core-3.1.1.jar "$@"
