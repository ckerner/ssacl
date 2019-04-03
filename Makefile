GPFSDIR=$(shell dirname $(shell which mmlscluster))
CURDIR=$(shell pwd)
PYTHON=$(shell which python)
LOCLDIR=/usr/local/bin

install: python ssacl utils

update: purge_links ssacl python utils

ssacl:	.FORCE
	cp -fp $(CURDIR)/ssacl $(LOCLDIR)/ssacl

python:	.FORCE
	$(PYTHON) $(CURDIR)/setup.py install

utils:	.FORCE
	cp -fp $(CURDIR)/backup_acls.sh $(LOCLDIR)/backup_acls.sh
	cp -fp $(CURDIR)/backup_acls.py $(LOCLDIR)/backup_acls.py

clean:
	rm -f $(LOCLDIR)/ssacl
	rm -f $(LOCLDIR)/backup_acls.sh
	rm -f $(LOCLDIR)/backup_acls.py

purge_links:
	rm -f ${LOCLDIR}/ssacl
	rm -f $(LOCLDIR)/backup_acls.sh
	rm -f $(LOCLDIR)/backup_acls.py

.FORCE:


