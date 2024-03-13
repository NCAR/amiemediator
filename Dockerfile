ARG PYTHON_QUALIFIER=:3.9-slim-bullseye
FROM python${PYTHON_QUALIFIER}

USER root

RUN apt-get -y --allow-releaseinfo-change update && \
    apt-get -y install \
      git

ARG PACKAGE=amiemediator
ARG IMAGE=ghcr.io/ncar/amiemediator
ARG IMAGE_VERSION=snapshot
ARG BRANCH=main
ARG PACKAGE_DIR=/usr/local/amiemediator

#
# Define the timezone via the TZ build arg.
#
ARG TZ=America/Denver

#
# We define a default non-root user to run the container as. This can be
# used for testing, etc.
#
ARG PYUSER=pyuser
ARG PYUSERID=900
ARG PYGROUP=pyuser
ARG PYGROUPID=900

ENV TZ=${TZ} \
    PACKAGE=amiemediator \
    PACKAGE_DIR=/usr/local/amiemediator \
    PYUSER=${PYUSER} \
    PYUSERID=${PYUSERID} \
    PYGROUP=${PYGROUP} \
    PYGROUPID=${PYGROUPID} \
    PYTHONPYCACHEPREFIX=/tmp \
    PYTHONPATH=${PACKAGE_DIR}/src

#RUN pip install pdoc
#RUN pip install pdoc-markdown
#    python3 -m pip install --upgrade build ; \
#    python3 -m build


RUN mkdir -p ${PACKAGE_DIR} \
             ${PACKAGE_DIR}/bin \
             ${PACKAGE_DIR}/src \
             ${PACKAGE_DIR}/test

COPY config.ini pip-packages \
              ${PACKAGE_DIR}/
COPY bin      ${PACKAGE_DIR}/bin/
COPY src      ${PACKAGE_DIR}/src
COPY tests    ${PACKAGE_DIR}/tests/
COPY runtests ${PACKAGE_DIR}/

RUN pip install --upgrade pip
RUN while read pkg ; do \
        pip install --root-user-action=ignore ${pkg} ; \
    done < ${PACKAGE_DIR}/pip-packages

WORKDIR ${PACKAGE_DIR}

#
# Set up timezone.
# Set up non-root user.
#
RUN set -e ; \
    rm -f /etc/localtime ; \
    ln -s /usr/share/zoneinfo/${TZ} /etc/localtime ; \
    cp /etc/localtime /usr/local/etc/localtime ; \
    echo "${TZ}" >/usr/local/etc/TZ ; \
    POSIX_TZ=`tr '\000' '\n' </etc/localtime | tail -1 | \
                   sed 's/^\([^,]*\).*/\1    /'` ; \
    echo ${POSIX_TZ} > /usr/local/etc/POSIX_TZ ; \
    addgroup --gid $PYUSERID $PYUSER ; \
    adduser --disabled-password \
            --uid $PYUSERID \
            --gid $PYGROUPID \
            --gecos "PY package user" \
            --home /home/$PYUSER \
            --shell /bin/bash \
            $PYUSER ; \
    chown -R $PYUSERID:$PYGROUPID ${PACKAGE_DIR}

USER $PYUSER

#RUN cd ${PACKAGE_DIR}
#RUN    /usr/local/sweet/bin/gendoc -v >gendoc/.log 2>&1 ; \
#    chown -R $MYSQL_USER:$MYSQL_GROUP gendoc


#CMD [ "python", "/usr/local/amie-sam-mediator/bin/amie" ]
CMD [ "/bin/bash" ]
