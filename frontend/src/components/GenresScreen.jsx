import { useEffect, useState } from 'react';
import { genreService } from '../services';

const GenresScreen = () => {
  const [genres, setGenres] = useState([]);
  const [name, setName] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editingName, setEditingName] = useState('');
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const data = await genreService.getAll();
      setGenres(data);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await genreService.create({ "name": name });
      setName('');
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  const startEdit = (id, currentName) => {
    setEditingId(id);
    setEditingName(currentName);
  };

  const handleUpdate = async (id) => {
    try {
      await genreService.update(id, { name: editingName });
      setEditingId(null);
      setEditingName('');
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar género?')) return;
    try {
      await genreService.remove(id);
      await load();
    } catch (e) {
      if (e.message.includes('assigned to one or more artists')) {
        setError('No se puede eliminar el género porque está asignado a uno o más artistas.');
      } else {
        setError(e.message);
      }
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Géneros</h2>
      {error && (
        <div className="bg-red-100 text-red-800 p-2 mb-4 rounded">
          {error}
        </div>
      )}
      <form onSubmit={handleCreate} className="flex mb-4">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nuevo género"
          className="flex-1 border p-2 mr-2 rounded"
        />
        <button
          type="submit"
          className="bg-green-500 text-white px-4 py-2 rounded"
        >
          Agregar
        </button>
      </form>
      <table className="w-full border">
        <thead>
          <tr>
            <th className="border px-2 py-1 text-left">Nombre</th>
            <th className="border px-2 py-1">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {genres.map((g) => (
            <tr key={g.id}>
              <td className="border px-2 py-1">
                {editingId === g.id ? (
                  <input
                    className="border p-1 w-full rounded"
                    value={editingName}
                    onChange={(e) => setEditingName(e.target.value)}
                  />
                ) : (
                  g.name
                )}
              </td>
              <td className="border px-2 py-1 text-center">
                {editingId === g.id ? (
                  <>
                    <button
                      type="button"
                      className="bg-blue-500 text-white px-2 py-1 mr-2 rounded"
                      onClick={() => handleUpdate(g.id)}
                    >
                      Guardar
                    </button>
                    <button
                      type="button"
                      className="bg-gray-300 px-2 py-1 rounded"
                      onClick={() => setEditingId(null)}
                    >
                      Cancelar
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      className="bg-blue-500 text-white px-2 py-1 mr-2 rounded"
                      onClick={() => startEdit(g.id, g.name)}
                    >
                      Editar
                    </button>
                    <button
                      type="button"
                      className="bg-red-500 text-white px-2 py-1 rounded"
                      onClick={() => handleDelete(g.id)}
                    >
                      Eliminar
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default GenresScreen;
