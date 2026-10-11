from xarm.wrapper import XArmAPI

def safe_session(boundary):
    # boundary = [x_max, x_min, y_max, y_min, z_max, z_min]
    if len(boundary) != 6:
        raise ValueError("A fronteira precisa de 6 valores")

    arm = XArmAPI('192.168.1.176', is_radian=False)

    def verificar(nome, codigo):
        if codigo != 0:
            raise RuntimeError(f"{nome} falhou: código {codigo}")

    verificar("Limpar avisos", arm.clean_warn())
    verificar("Limpar erros", arm.clean_error())
    verificar("Limite das juntas", arm.set_reduced_max_joint_speed(54))
    verificar("Limite do TCP", arm.set_reduced_max_tcp_speed(150))
    verificar("Fronteira do TCP", arm.set_reduced_tcp_boundary(boundary))
    verificar("Modo reduzido", arm.set_reduced_mode(True))
    verificar("Ativar fronteira", arm.set_fence_mode(True))
    verificar("Ativar movimento", arm.motion_enable(enable=True))
    verificar("Definir modo", arm.set_mode(0))
    verificar("Definir estado", arm.set_state(0))

    return arm