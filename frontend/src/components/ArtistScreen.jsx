import { useEffect, useState } from 'react';
import { artistService } from '../services';

const ArtistScreen = () => {
  const [artists, setArtists] = useState([]);
  const [genres, setGenres] = useState([]);
  const [form, setForm] = useState({ name: '', country: '', genre: [] });
  const [editingId, setEditingId] = useState(null);

  const loadData = async () => {
    try {
      const [artistData, genreData] = await Promise.all([
        artistService.getArtists(),
        artistService.getGenres(),
      ]);
      setArtists(artistData);
      setGenres(genreData);
    } catch (err) {
      console.error('Error loading data', err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleChange = (e) => {
    const { name, value, selectedOptions } = e.target;
    if (name === 'genre') {
      const values = Array.from(selectedOptions, (opt) => opt.value);
      setForm((prev) => ({ ...prev, genre: values }));
    } else {
      setForm((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await artistService.updateArtist(editingId, form);
      } else {
        await artistService.createArtist(form);
      }
      setForm({ name: '', country: '', genre: [] });
      setEditingId(null);
      await loadData();
    } catch (err) {
      console.error('Error saving artist', err);
    }
  };

  const handleEdit = (artist) => {
    setEditingId(artist.id);
    setForm({ name: artist.name, country: artist.country, genre: artist.genre });
  };

  const handleDelete = async (id) => {
    if (!confirm('¿Eliminar artista?')) return;
    try {
      await artistService.deleteArtist(id);
      await loadData();
    } catch (err) {
      console.error('Error deleting artist', err);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Gestión de Artistas</h2>

      <form onSubmit={handleSubmit} className="mb-6 space-y-4">
        <input
          type="text"
          name="name"
          placeholder="Nombre"
          value={form.name}
          onChange={handleChange}
          className="border p-2 w-full"
          required
        />
        <input
          type="text"
          name="country"
          placeholder="País"
          value={form.country}
          onChange={handleChange}
          className="border p-2 w-full"
          required
        />
        <select
          multiple
          name="genre"
          value={form.genre}
          onChange={handleChange}
          className="border p-2 w-full"
        >
          {genres.map((g) => (
            <option key={g.id} value={g.name}>
              {g.name}
            </option>
          ))}
        </select>
        <button
          type="submit"
          className="bg-green-500 text-white px-4 py-2 rounded"
        >
          {editingId ? 'Actualizar' : 'Crear'}
        </button>
      </form>

      <table className="w-full border">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2 border">Nombre</th>
            <th className="p-2 border">País</th>
            <th className="p-2 border">Géneros</th>
            <th className="p-2 border">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {artists.map((a) => (
            <tr key={a.id} className="text-center">
              <td className="border p-2">{a.name}</td>
              <td className="border p-2">{a.country}</td>
              <td className="border p-2">{Array.isArray(a.genre) ? a.genre.join(', ') : ''}</td>
              <td className="border p-2 space-x-2">
                <button
                  onClick={() => handleEdit(a)}
                  className="bg-blue-500 text-white px-2 py-1 rounded"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(a.id)}
                  className="bg-red-500 text-white px-2 py-1 rounded"
                >
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ArtistScreen;
