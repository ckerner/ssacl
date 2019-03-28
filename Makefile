GPFSDIR=$(shell dirname $(shell which mmlscluster))
CURDIR=$(shell pwd)
PYTHON=$(shell which python)
LOCLDIR=/usr/local/bin

install: python ssacl

update: purge_links ssacl python

ssacl:	.FORCE
	cp -fp $(CURDIR)/ssacl $(LOCLDIR)/ssacl

python:	.FORCE
	$(PYTHON) $(CURDIR)/setup.py install

clean:
	rm -f $(LOCLDIR)/ssacl

purge_links:
	rm -f ${LOCLDIR}/ssacl

.FORCE:


