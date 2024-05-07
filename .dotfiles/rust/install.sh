while IFS= read -r package; do
    cargo install "$package"
done < requirements.txt
