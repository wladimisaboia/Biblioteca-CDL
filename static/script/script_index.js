function updateDate() {
    var dateContainer = document.getElementById('date-container');
    var currentDate = new Date();
    var dateString = currentDate.toLocaleDateString('pt-BR');
    dateContainer.innerHTML = 'Data: ' + dateString;
}

setInterval(updateDate, 1000);
updateDate();

function salvarLinha(numeroOrdem) {
    localStorage.setItem("ordem-" + numeroOrdem, numeroOrdem);
    alert("Visitante " + numeroOrdem + " salvo!");
}

window.onload = function () {
    carregarVisitas();
};

function carregarVisitas() {
    var storedClientsTable = document.getElementById("stored-clients-table").getElementsByTagName('tbody')[0];

    fetch('/visitas', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(data => {
            storedClientsTable.innerHTML = "";

            data.forEach(client => {
                var row = storedClientsTable.insertRow(-1);
                var cell1 = row.insertCell(0);
                var cell2 = row.insertCell(1);
                var cell3 = row.insertCell(2);
                var cell4 = row.insertCell(3);

                cell1.innerHTML = client.ordem;
                cell2.innerHTML = client.data;
                cell3.innerHTML = client.tipo_visitante;
                cell4.innerHTML = client.atividades;
            });
        })
        .catch(error => console.error('Erro:', error));
}

function adicionarLinha(turno) {
    var table = document.getElementById("attendance-table");
    var lastRowNumber = table.rows.length;

    var newRow = table.insertRow(-1);

    for (var i = 0; i < table.rows[0].cells.length; i++) {
        var cell = newRow.insertCell(i);

        if (i === 0) {
            cell.innerHTML = lastRowNumber;
        } else if (i === table.rows[0].cells.length - 1) {
            cell.innerHTML = `<button onclick="salvarLinhaServidor(${lastRowNumber}, '${turno}')">Salvar</button>`;
        } else if (i === 1) {
            cell.innerHTML = `
                <select name="atividade${lastRowNumber}_A">
                    <option value="0">Selecione</option>
                    <option value="A">Aluno Extensão</option>
                    <option value="B">Aluno Graduação</option>
                    <option value="C">Aluno Pós-Graduação</option>
                    <option value="D">Corpo Docente</option>
                    <option value="E">Diretor</option>
                    <option value="F">Funcionário</option>
                    <option value="G">Gestor</option>
                    <option value="H">Institucional</option>
                    <option value="I">Visitante</option>
                </select>`;
        } else {
            cell.innerHTML = `<td class="radio-container"><label><input type="checkbox" name="atividade${lastRowNumber}_${String.fromCharCode(65 + i - 1)}" value="${String.fromCharCode(65 + i - 1)}"></label></td>`;
        }
    }
}

function salvarLinhaServidor(numeroOrdem, turno) {
    var tipoVisitante = document.querySelector(`select[name="atividade${numeroOrdem}_A"]`).value;

    var atividades = [];
    for (var i = 1; i <= 8; i++) {
        if (document.querySelector(`input[name="atividade${numeroOrdem}_${String.fromCharCode(64 + i)}"]:checked`)) {
            atividades.push(String.fromCharCode(64 + i));
        }
    }

    // Adicione esta linha para obter o login
    var login = localStorage.getItem('login');  // substitua 'login' pelo valor correto

    fetch('/salvar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `numero_ordem=${numeroOrdem}&tipo_visitante=${tipoVisitante}&atividades=${atividades.join(',')}&login=${login}&turno=${turno}`,
    })
        .then(response => response.json())
        .then(data => {
            console.log(data.mensagem);
            alert(data.mensagem);
            carregarClientesArmazenados();
        })
        .catch(error => console.error('Erro:', error));
}


function gerarRelatorio() {
    var startDate = document.getElementById('start-date').value;
    var endDate = document.getElementById('end-date').value;

    fetch('/gerar_relatorio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `start-date=${startDate}&end-date=${endDate}`,
    })
        .then(response => response.json())
        .then(data => {
            if (data.filename) {
                var link = document.createElement('a');
                link.href = data.filename;
                link.download = 'relatorio.csv';
                document.body.appendChild(link);

                link.click();

                document.body.removeChild(link);
            } else {
                alert('Erro ao gerar o relatório');
            }
        })
        .catch(error => console.error('Erro:', error));
}

function sair() {
    window.location.href = '/sair';
}
