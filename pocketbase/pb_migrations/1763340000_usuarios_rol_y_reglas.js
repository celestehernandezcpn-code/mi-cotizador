/// <reference path="../pb_data/types.d.ts" />
// Agrega a "users" el campo rol (usuario | admin) y el campo desactivado,
// y define las reglas: solo un admin activo puede listar, desactivar o resetear cuentas.
migrate(
  (app) => {
    const users = app.findCollectionByNameOrId("users");

    users.fields.add(
      new SelectField({
        name: "rol",
        values: ["usuario", "admin"],
        maxSelect: 1,
        required: false,
      })
    );
    users.fields.add(new BoolField({ name: "desactivado" }));

    // Admin = rol "admin" y cuenta no desactivada (vale también para tokens ya emitidos)
    const admin = '@request.auth.rol = "admin" && @request.auth.desactivado = false';
    const sinPrivilegios =
      "@request.body.rol:isset = false && @request.body.desactivado:isset = false";

    // Solo los admins ven el listado completo; cada usuario puede ver su propia ficha.
    users.listRule = admin;
    const propiaActiva = "id = @request.auth.id && @request.auth.desactivado = false";
    users.viewRule = "(" + propiaActiva + ") || (" + admin + ")";
    // Registro público, pero nadie puede asignarse rol ni estado al registrarse.
    users.createRule = sinPrivilegios;
    // Un admin puede modificar cualquier cuenta; el resto, solo la suya y sin tocar rol/estado.
    users.updateRule =
      "(" + admin + ") || (" + propiaActiva + " && " + sinPrivilegios + ")";
    // Nadie borra cuentas desde la API (solo el superusuario desde el panel de PocketBase).
    users.deleteRule = null;
    // Un admin puede cambiar la contraseña de otras cuentas sin conocer la anterior.
    users.manageRule = admin;
    // Las cuentas desactivadas no pueden iniciar sesión.
    users.authRule = "desactivado = false";

    return app.save(users);
  },
  (app) => {
    const users = app.findCollectionByNameOrId("users");
    users.fields.removeByName("rol");
    users.fields.removeByName("desactivado");
    users.listRule = "id = @request.auth.id";
    users.viewRule = "id = @request.auth.id";
    users.createRule = "";
    users.updateRule = "id = @request.auth.id";
    users.deleteRule = "id = @request.auth.id";
    users.manageRule = null;
    users.authRule = "";
    return app.save(users);
  }
);
