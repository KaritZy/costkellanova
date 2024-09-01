document.addEventListener('DOMContentLoaded', () => {
  // Referencias a elementos del DOM
  const form = document.getElementById('add-equipment-form');
  const equiposList = document.getElementById('equipos-list');
  const adminForm = document.getElementById('adminForm');  // Formulario de autenticación de administrador
  let currentFolio = null;

  // Función para abrir el modal de autenticación
  function openModal(folio) {
      console.log('Folio recibido:', folio);  // Depuración: Verifica el folio recibido
      currentFolio = folio;  // Guardar el folio actual
      document.getElementById('authModal').style.display = 'block';
      adminForm.action = '/responder/' + folio;  // Configurar la acción del formulario con el folio correcto
      console.log('Formulario configurado para enviar a:', adminForm.action);  // Depuración: Verifica la URL de acción
  }

  // Función para cerrar el modal de autenticación
  function closeModal() {
      document.getElementById('authModal').style.display = 'none';
  }

  // Cargar equipos desde localStorage y actualizar la lista
  function updateEquiposList() {
      equiposList.innerHTML = '';
      let equipos = JSON.parse(localStorage.getItem('equipos')) || [];
      equipos.forEach((equipo, index) => {
          let li = document.createElement('li');
          li.textContent = equipo.name;
          li.onclick = () => {
              let components = prompt('Ingrese componentes separados por coma:', equipo.components.join(', '));
              if (components !== null) {
                  equipos[index].components = components.split(',').map(comp => comp.trim());
                  localStorage.setItem('equipos', JSON.stringify(equipos));
                  updateEquiposList();
              }
          };
          equiposList.appendChild(li);
      });
  }

  // Manejar el envío del formulario para agregar equipos
  form.addEventListener('submit', (event) => {
      event.preventDefault();
      const equipmentName = document.getElementById('equipment-name').value;
      if (equipmentName) {
          // Agregar equipo a localStorage
          let equipos = JSON.parse(localStorage.getItem('equipos')) || [];
          equipos.push({ name: equipmentName, components: [] });
          localStorage.setItem('equipos', JSON.stringify(equipos));

          // Actualizar la lista de equipos
          updateEquiposList();
          form.reset();
      }
  });

  // Inicializar la lista de equipos al cargar la página
  updateEquiposList();

  // Manejar el envío del formulario de autenticación del administrador
  adminForm.addEventListener('submit', (event) => {
      event.preventDefault();
      // Validar que el formulario tenga un folio configurado en la acción
      if (adminForm.action.includes('/responder/') && currentFolio !== null) {
          adminForm.submit();  // Enviar el formulario
      } else {
          alert('Error: Folio no configurado correctamente.');
      }
  });
});
