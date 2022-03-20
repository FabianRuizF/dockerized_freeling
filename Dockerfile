FROM fabiancrruiz/freeling:4.2
RUN apt update
RUN apt-get install -y locales locales-all
RUN export LC_ALL=es_ES.UTF-8
RUN export LANG=es_ES.UTF-8
#COPY es.cfg es.cfg
#RUN mv es.cfg /usr/local/share/freeling/config/es_nomwe.cfg

#COPY en.cfg en.cfg
#RUN mv en.cfg /usr/local/share/freeling/config/en.cfg

WORKDIR /root
EXPOSE 50005
#CMD [ "analyze", "-f", "es_nomwe.cfg", "--server", "-p"," 50005","--outlv"," parsed"]
#CMD [ "analyze", "-f", "es.cfg", "--server", "-p"," 50005","--outlv","tagged"]
#CMD [ "analyze", "-f", "en.cfg", "--server", "-p"," 50005","--outlv","coref","--output","xml"]
CMD [ "analyze", "-f", "it.cfg", "--server", "-p"," 50005","--outlv","tagged"]
#CMD echo 'Hello world' | analyze -f en.cfg | grep -c 'world world NN 1
