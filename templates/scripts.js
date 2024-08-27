document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('add-equipment-form');
    const equiposList = document.getElementById('equipos-list');
  
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
  
    // Manejar el envío del formulario
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const equipmentName = document.getElementById('equipment-name').value;
      if (equipmentName) {
        // Agregar equipo a localStorage
        let equipos = JSON.parse(localStorage.getItem('equipos')) || [];
        equipos.push({ name: equipmentName, components: [] });
        localStorage.setItem('equipos', JSON.stringify(equipos));
        
        // Actualizar la lista
        updateEquiposList();
        form.reset();
      }
    });
  
    // Cargar lista al iniciar
    updateEquiposList();
  });
  