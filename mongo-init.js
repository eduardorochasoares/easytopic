db.createUser(
        {
            user: "root",
            pwd: "MongoDB2019!",
            roles: [
                {
                    role: "root",
                    db: "topic_segmentation"
                }
            ]
        }
);
