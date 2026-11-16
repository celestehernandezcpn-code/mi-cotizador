/// <reference path="../pb_data/types.d.ts" />
// Colección "consultas": historial de conversiones de cada usuario.
// Cada usuario solo crea y lee las suyas; nadie las modifica ni las borra por la API.
migrate(
  (app) => {
    const users = app.findCollectionByNameOrId("users");

    const activo = "@request.auth.desactivado = false";
    const propia = "usuario = @request.auth.id && " + activo;

    const consultas = new Collection({
      type: "base",
      name: "consultas",
      fields: [
        {
          type: "relation",
          name: "usuario",
          required: true,
          collectionId: users.id,
          maxSelect: 1,
          cascadeDelete: true,
        },
        // Sin "required": un monto o resultado igual a 0 es válido
        { type: "number", name: "monto" },
        { type: "number", name: "cotizacion" },
        { type: "number", name: "resultado" },
        // La fecha y hora la fija el servidor al crear el registro
        { type: "autodate", name: "fecha", onCreate: true, onUpdate: false },
      ],
      indexes: ["CREATE INDEX idx_consultas_usuario ON consultas (usuario)"],
      listRule: propia,
      viewRule: propia,
      createRule:
        '@request.auth.id != "" && ' + activo + " && @request.body.usuario = @request.auth.id",
      updateRule: null,
      deleteRule: null,
    });

    return app.save(consultas);
  },
  (app) => {
    return app.delete(app.findCollectionByNameOrId("consultas"));
  }
);
