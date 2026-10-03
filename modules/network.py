import subprocess
def run_command(command):
    try: return subprocess.check_output(command,shell=True,text=True,stderr=subprocess.STDOUT,timeout=20).strip()
    except Exception as e: return "No disponible: "+str(e)
def get_ip(): return run_command("ipconfig")
def get_interfaces(): return run_command("netsh interface show interface")
def scan_wifi(): return run_command("netsh wlan show networks mode=bssid")
def connection_status(): return run_command("netsh interface show interface")
def network_info(): return run_command("ipconfig /all")
def network_menu():
    from core.ui import module_banner,menu_box,clear
    from core.navigation import check_navigation
    actions={"1":("IP del equipo",get_ip),"2":("Interfaces de red",get_interfaces),"3":("Redes WiFi",scan_wifi),"4":("Estado de conexion",connection_status),"5":("Informacion de red",network_info)}
    while True:
        clear();module_banner("RED");menu_box("1. Ver IP\n2. Ver interfaces de red\n3. Escanear WiFi\n4. Estado de conexion\n5. Informacion de red\n\n00. Inicio\n0. Volver","RED")
        o=input("\nSeleccione una opcion: ");nav=check_navigation(o)
        if nav=="home": return "home"
        if nav=="back": return "back"
        if o in actions:
            title,fn=actions[o];print("\n"+title+":\n\n"+fn());input("\nENTER para continuar")
