from application import Application

#returns a letter that defines an application, we'll use it to have
#a short representation of queues as a sequence of letters
def encode_application(app):
    if app.app == "BTIO":
        if app.nodes == 32:
            return "A"
        elif app.nodes == 64:
            return "B"
        else:
            assert False
    elif app.app == "HACC":
        return "C"
    elif app.app == "IOR-MPIIO":
        return "D"
    elif app.app == "IOR-POSIX":
        if app.nodes == 16:
            return "E"
        elif app.nodes == 64:
            return "F"
        else:
            assert False
    elif app.app == "MADBENCH2":
        return "G"
    elif app.app == "S3ASIM":
        return "H"
    elif app.app == "S3D-IO":
        return "I"
    else:
        print(app.app)
        assert False
