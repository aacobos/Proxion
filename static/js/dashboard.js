// Gráfico mensal
const ctx = document.getElementById('monthlyChart').getContext('2d');
const monthlyChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        datasets: [{
            label: 'Vistorias Realizadas',
            data: [12, 19, 15, 25, 22, 30],
            backgroundColor: '#009999',
            borderColor: '#008080',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Quantidade de Vistorias'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Meses'
                }
            }
        }
    }
});

// Função para carregar dados do localStorage
function loadDashboardData() {
    const reports = JSON.parse(localStorage.getItem('reports') || '[]');
    
    // Atualizar contador de vistorias recentes
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    const recentInspections = reports.filter(report => 
        new Date(report.report.serviceDate) >= thirtyDaysAgo
    );
    
    document.getElementById('recentInspectionsCount').textContent = recentInspections.length;
    
    // Atualizar contador de equipamentos ativos
    const uniqueEquipment = new Set();
    reports.forEach(report => {
        report.equipment.forEach(equip => {
            uniqueEquipment.add(equip.serialNumber);
        });
    });
    document.getElementById('activeEquipmentCount').textContent = uniqueEquipment.size;
    
    // Atualizar contador de alertas
    const maintenanceAlerts = reports.filter(report => {
        const serviceDate = new Date(report.report.serviceDate);
        const daysSinceService = Math.floor((new Date() - serviceDate) / (1000 * 60 * 60 * 24));
        return daysSinceService > 90;
    });
    
    document.getElementById('maintenanceAlertsCount').textContent = maintenanceAlerts.length;

    // Carregar vistorias realizadas e pendentes
    const completedInspectionsList = document.getElementById('completedInspections');
    const pendingInspectionsList = document.getElementById('pendingInspections');
    
    completedInspectionsList.innerHTML = '';
    pendingInspectionsList.innerHTML = '';

    // Ordenar relatórios por data
    reports.sort((a, b) => new Date(b.report.serviceDate) - new Date(a.report.serviceDate));

    reports.forEach(report => {
        const listItem = document.createElement('li');
        const date = new Date(report.report.serviceDate).toLocaleDateString('pt-BR');
        const status = report.report.status || 'Pendente';
        
        listItem.innerHTML = `
            <div>
                <strong>${report.report.location || 'Local não especificado'}</strong>
                <div class="inspection-date">${date}</div>
            </div>
            <span class="inspection-status ${status === 'Concluído' ? 'status-completed' : 'status-pending'}">
                ${status}
            </span>
        `;

        if (status === 'Concluído') {
            completedInspectionsList.appendChild(listItem);
        } else {
            pendingInspectionsList.appendChild(listItem);
        }
    });
}

// Função para carregar o nome do usuário
function loadUserName() {
    const user = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const userName = user.name || 'Usuário';
    document.getElementById('userName').textContent = userName;
}

// Carregar dados ao iniciar
loadDashboardData();
loadUserName();