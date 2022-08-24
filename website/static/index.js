function deleteNote(noteId) {
    fetch("/delete-note", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
        window.location.href= "/notes";
    });
}

function deleteFriend(personId) {
    fetch("/delete-friend", {
        method: "POST",
        body: JSON.stringify({ personId: personId }),
    }).then((_res) => {
        window.location.href= "/friends";
    });
}