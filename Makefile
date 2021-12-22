deploy :
	cd ansible && ansible-playbook -i hosts -u amber seefood.yml