function switchStory(storyIndex) {
    const containers = document.querySelectorAll('.story-container');
    containers.forEach(container => container.style.display = 'none');

    const selectedStory = document.getElementById(`story-${storyIndex}`);
    if (selectedStory) {
        selectedStory.style.display = 'block';


        updateGlobalCriticalBadge(selectedStory);
    }
}


function updateGlobalCriticalBadge(storyContainer) {
    const globalBadge = document.getElementById('global-critical-badge');
    if (!globalBadge) return;


    const hasCritical = storyContainer.getAttribute('data-has-critical') === 'true';

    if (hasCritical) {
        globalBadge.style.display = 'inline-block';
    } else {
        globalBadge.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const firstStory = document.querySelector('.story-container[style*="display: block"], .story-container:not([style*="display: none"])');
    if (firstStory) {
        updateGlobalCriticalBadge(firstStory);
    }
});


function switchTab(storyIndex, tabName) {

    const storyContainer = document.getElementById(`story-${storyIndex}`);
    if (!storyContainer) return;

    const contents = storyContainer.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));


    const buttons = storyContainer.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));

    const selectedTab = document.getElementById(`${tabName}-view-${storyIndex}`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }

    event.target.classList.add('active');
}


function acceptFlag(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        row.style.background = '#d4edda';
        setTimeout(() => {
            row.style.background = '';
        }, 2000);
    }
}

function rejectFlag(rowId) {
    if (confirm('Are you sure you want to remove this flag?')) {
        const row = document.getElementById(rowId);
        if (row) row.remove();
    }
}


function acceptSkill(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        row.style.background = '#d4edda';
        setTimeout(() => {
            row.style.background = '';
        }, 2000);
    }
}

function removeSkill(rowId) {
    if (confirm('Are you sure you want to remove this skill tag?')) {
        const row = document.getElementById(rowId);
        if (row) row.remove();
    }
}

function submitFeedback() {
    const feedback = document.getElementById('feedback-text').value;

    if (!feedback.trim()) {
        alert('Please enter some feedback');
        return;
    }
    alert('Thank you for your feedback!\n\nNote: In a production system, this would be saved to the backend.');

    document.getElementById('feedback-text').value = '';
}
