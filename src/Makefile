RPM_PACKAGE_NAME = yum-plugin-autoskip

NAME      := $(RPM_PACKAGE_NAME)

.PHONY: all install

install:
	install -m 0755 -d $(DESTDIR)/usr/lib/yum-plugins
	install -m 0755 -d $(DESTDIR)/usr/share/doc/$(NAME)
	install -m 0755 -d $(DESTDIR)/etc/yum/mirrors
	install -m 0755 -d $(DESTDIR)/etc/yum/pluginconf.d

	install -m 0644 -pt $(DESTDIR)/usr/lib/yum-plugins autoskip.py
	install -m 0644 -pt $(DESTDIR)/etc/yum/pluginconf.d autoskip.conf
	install -m 0644 -pt $(DESTDIR)/usr/share/doc/$(NAME) COPYING CHANGELOG

	touch  $(DESTDIR)/usr/lib/yum-plugins/autoskip.py{c,o}

