from cliente.cliente import Clientes

class App:
    def __init__(self):
        self.main()

    def limpiarPantalla(self):
        print("\033c")

    def esperarTecla(self):
        input("\nPresiona cualaquier tecla para continuar...")

    def menuClientes(self):
        while True:
            self.limpiarPantalla()
            print("========================================")
            print("   ...::: MENÚ DE CLIENTES :::...        ")
            print("========================================")
            print("1. Consultar clientes")
            print("2. Insertar nuevo cliente")
            print("3. Actualizar cliente")
            print("4. Eliminar cliente")
            print("5. Regresar al menú principal")
            
            menu = input("\nElige una opción (1-5): ")
            
            match menu:
                case "1":
                    self.limpiarPantalla()
                    print("--- LISTA DE CLIENTES REGISTRADOS ---")
                    clientes = Clientes.consultar()
                    if clientes:
                        for c in clientes:
                            print(f"ID: {c[0]} | Razón Social: {c[1]} | Contacto: {c[2]} | Tel: {c[3]} | Email: {c[4]}")
                    else:
                        print("No hay clientes registrados o ocurrió un error.")
                    self.esperarTecla()

                case "2":
                    self.limpiarPantalla()
                    print("--- REGISTRAR NUEVO CLIENTE ---")
                    razon = input("Razón social: ")
                    contacto = input("Persona de contacto: ")
                    telefono = input("Teléfono: ")
                    email = input("Email: ")
                    
                    nuevo_cliente = Clientes(razon, contacto, telefono, email)
                    if nuevo_cliente.insertar():
                        print("\n¡Cliente registrado exitosamente!")
                    else:
                        print("\nError al registrar el cliente.")
                    self.esperarTecla()

                case "3":
                    self.limpiarPantalla()
                    print("--- ACTUALIZAR CLIENTE ---")
                    id_cliente = input("Ingresa el ID del cliente a actualizar: ")
                    razon = input("Nueva razón social: ")
                    contacto = input("Nueva persona de contacto: ")
                    telefono = input("Nuevo teléfono: ")
                    email = input("Nuevo email: ")
                    
                    cliente_act = Clientes(razon, contacto, telefono, email)
                    if cliente_act.actulizar(id_cliente):
                        print("\n¡Cliente actualizado con éxito!")
                    else:
                        print("\nError al actualizar el cliente.")
                    self.esperarTecla()

                case "4":
                    self.limpiarPantalla()
                    print("--- ELIMINAR CLIENTE ---")
                    id_cliente = input("Ingresa el ID del cliente que deseas eliminar: ")
                    if Clientes.eliminar(id_cliente):
                        print("\n¡Cliente eliminado correctamente!")
                    else:
                        print("\nError al eliminar el cliente.")
                    self.esperarTecla()

                case "5":
                    break

                case _:
                    print("\nOpción no válida. Inténtalo de nuevo.")
                    self.esperarTecla()

    def main(self):
        while True:
            self.limpiarPantalla()
            print(".:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.")
            print("...::: SISTEMA DE ÓRDENES ECLIPSE :::...")
            print(".:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.")
            print("1. Gestionar Clientes")
            print("2. Salir")
            
            opciones = input("\nElige una opción: ")
            
            match opciones:
                case "1": 
                    self.menuClientes()
                case "2":
                    print("\n¡Gracias por usar el sistema! Saliendo...")
                    break
                case _:
                    print("\nOpción no válida, intenta de nuevo.")
                    self.esperarTecla()

if __name__ == "__main__":
    app = App()