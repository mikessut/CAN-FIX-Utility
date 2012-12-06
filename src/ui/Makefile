UIFILES = main_ui.py connect_ui.py firmware_ui.py

all: $(UIFILES)

run: all
	./canfix.py

%_ui.py: %.ui
	pyuic4 -o $@ $<

clean:
	rm $(UIFILES) *.pyc

